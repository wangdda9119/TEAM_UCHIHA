
"""
Minimal FAISS index utility.
Store path controlled by VECTOR_DIR (.env).
"""
from pathlib import Path
import numpy as np
import faiss
from backend.core.config import settings

class SimpleFaissStore:
    def __init__(self, dim: int = 384, index_name: str = "faiss.index"):
        self.dim = dim
        self.index_path = Path(settings.vector_dir) / index_name
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.index = faiss.IndexFlatL2(self.dim)

    def add(self, vecs: np.ndarray):
        assert vecs.ndim == 2 and vecs.shape[1] == self.dim
        self.index.add(vecs.astype("float32"))

    def search(self, q: np.ndarray, k: int = 5):
        assert q.ndim == 2 and q.shape[1] == self.dim
        D, I = self.index.search(q.astype("float32"), k)
        return D, I

    def save(self):
        faiss.write_index(self.index, str(self.index_path))

    def load(self):
        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
