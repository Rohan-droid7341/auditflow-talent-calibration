import os
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

from src.config import CHROMA_DIR, DOCS_DIR, HF_TOKEN, HF_EMBEDDING_MODEL, has_hf_token

class HuggingFaceAPIEmbeddingFunction(EmbeddingFunction):
    """
    Calls the Hugging Face Serverless Inference API for embeddings.
    Zero local compute / PyTorch overhead, 100% free.
    """
    def __init__(self, api_token: str, model_name: str = HF_EMBEDDING_MODEL):
        self.api_token = api_token
        self.model_name = model_name
        self.api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.model_name}"
        self.headers = {"Authorization": f"Bearer {self.api_token}"}

    def __call__(self, input: Documents) -> Embeddings:
        response = requests.post(
            self.api_url,
            headers=self.headers,
            json={"inputs": input, "options": {"wait_for_model": True}},
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            # If input was a single string vs list of strings, handle dimensions
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], list):
                    return result
                return [result]
        # If API fails or rate-limits, raise or fall back
        raise RuntimeError(f"Hugging Face Inference API error {response.status_code}: {response.text}")

class LocalFallbackEmbeddingFunction(EmbeddingFunction):
    """
    Deterministic zero-cost fallback embedding function if HF_TOKEN is absent.
    Generates a deterministic 384-dimensional vector based on text token hashing.
    Ensures offline tests and CI passes without requiring external network.
    """
    def __call__(self, input: Documents) -> Embeddings:
        import hashlib
        embeddings = []
        for text in input:
            vec = [0.0] * 384
            words = text.lower().split()
            for word in words:
                h = int(hashlib.md5(word.encode()).hexdigest(), 16)
                idx = h % 384
                vec[idx] += 1.0
            norm = sum(x*x for x in vec) ** 0.5 or 1.0
            embeddings.append([x / norm for x in vec])
        return embeddings

def get_embedding_function() -> EmbeddingFunction:
    if has_hf_token():
        try:
            return HuggingFaceAPIEmbeddingFunction(HF_TOKEN, HF_EMBEDDING_MODEL)
        except Exception:
            return LocalFallbackEmbeddingFunction()
    return LocalFallbackEmbeddingFunction()

def get_chroma_client():
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_DIR))

def init_vector_store(force_reindex: bool = False):
    client = get_chroma_client()
    embedding_fn = get_embedding_function()
    
    if force_reindex:
        try:
            client.delete_collection("candidate_dossiers")
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name="candidate_dossiers",
        embedding_function=embedding_fn,
        metadata={"description": "Candidate dossiers and requisition specs for talent calibration"}
    )
    
    if collection.count() > 0 and not force_reindex:
        return collection
        
    # Ingest markdown files from DOCS_DIR
    documents = []
    metadatas = []
    ids = []
    doc_id = 0
    
    for file_path in DOCS_DIR.glob("*.md"):
        filename = file_path.name
        cand_id = "general"
        if "rohan" in filename:
            cand_id = "rohan_garg"
        elif "jordan" in filename:
            cand_id = "jordan_taylor"
        elif "priya" in filename:
            cand_id = "priya_sharma"
        elif "requisition" in filename:
            cand_id = "requisition"

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Chunk content by headers
        sections = content.split("## ")
        for i, section in enumerate(sections):
            text = section.strip()
            if not text:
                continue
            if not text.startswith("#"):
                text = "## " + text
                
            doc_id += 1
            documents.append(text)
            metadatas.append({
                "candidate_id": cand_id,
                "source_file": filename,
                "section_index": i
            })
            ids.append(f"doc_{cand_id}_{doc_id}")

    if documents:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    return collection

def query_candidate_evidence(candidate_id: str, query_text: str, n_results: int = 4) -> List[Dict[str, Any]]:
    client = get_chroma_client()
    embedding_fn = get_embedding_function()
    collection = client.get_or_create_collection("candidate_dossiers", embedding_function=embedding_fn)
    
    if collection.count() == 0:
        init_vector_store(force_reindex=True)
        collection = client.get_or_create_collection("candidate_dossiers", embedding_function=embedding_fn)

    results = collection.query(
        query_texts=[query_text],
        where={"candidate_id": candidate_id},
        n_results=min(n_results, max(1, collection.count()))
    )
    
    evidence = []
    if results and "documents" in results and results["documents"]:
        docs = results["documents"][0]
        metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
        dists = results["distances"][0] if "distances" in results and results["distances"] else [0.0] * len(docs)
        
        for doc, meta, dist in zip(docs, metas, dists):
            evidence.append({
                "text": doc,
                "source": meta.get("source_file", "unknown"),
                "relevance_distance": round(dist, 4)
            })
    return evidence
