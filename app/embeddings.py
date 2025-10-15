from sentence_transformers import SentenceTransformer
import numpy as np
from app.config import EMBEDDING_MODEL

class EmbeddingGenerator:
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts):
        arr = self.model.encode(texts, show_progress_bar=False)
        if isinstance(arr, np.ndarray):
            return arr.tolist()
        return [list(v) for v in arr]
