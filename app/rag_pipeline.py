from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.embeddings import EmbeddingGenerator
from app.groq_client import call_groq_llm
from app.config import QDRANT_HOST, QDRANT_PORT, VECTOR_COLLECTION, TOP_K
from rich import print as rprint

class RAGPipeline:
    def __init__(self, collection_name: str = VECTOR_COLLECTION):
        self.client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        self.embedder = EmbeddingGenerator()
        self.collection_name = collection_name

    def initialize_collection(self, chunks, collection_name: str = None):
        if not chunks:
            raise ValueError("No chunks to initialize collection.")
        vectors = self.embedder.embed_texts([c["text"] for c in chunks])
        dim = len(vectors[0])
        col = collection_name or self.collection_name
        rprint(f"[blue]Recreating collection:[/blue] {col} (dim={dim})")
        self.client.recreate_collection(
            collection_name=col,
            vectors_config=models.VectorParams(size=dim, distance=models.Distance.COSINE),
        )
        payload = [{"text": c["text"], "metadata": c.get("metadata", {})} for c in chunks]
        ids = list(range(len(vectors)))
        self.client.upload_collection(
            collection_name=col,
            vectors=vectors,
            payload=payload,
            ids=ids,
        )
        rprint("[green]Qdrant collection initialized[/green]")
        return col

    def retrieve(self, query: str, top_k: int = TOP_K, collection_name: str = None):
        vec = self.embedder.embed_texts([query])[0]
        col = collection_name or self.collection_name
        hits = self.client.search(collection_name=col, query_vector=vec, limit=top_k)
        return hits

    def answer_query(self, query: str, top_k: int = TOP_K, collection_name: str = None) -> dict[str, object]:
        hits = self.retrieve(query, top_k, collection_name)
        contexts = []
        for h in hits:
            payload = getattr(h, "payload", h["payload"] if isinstance(h, dict) and "payload" in h else {})
            text = payload.get("text", "")
            metadata = payload.get("metadata", {})
            contexts.append(f"---\n{metadata}\n{text[:1200]}\n")
        context_block = "\n".join(contexts)
        prompt = (
            "You are a company policy assistant. Use ONLY the provided context to answer.\n\n"
            f"CONTEXT:\n{context_block}\n\nQUESTION:\n{query}\n\n"
            "Answer succinctly and indicate which context slices you used."
        )
        generated = call_groq_llm(prompt)
        return {
            "answer": generated,
            "retrieved": [
                {
                    "score": getattr(h, "score", h["score"] if isinstance(h, dict) and "score" in h else None),
                    "payload": getattr(h, "payload", h["payload"] if isinstance(h, dict) and "payload" in h else None),
                }
                for h in hits
            ]
        }
