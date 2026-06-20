"""FAISS Vector Index Manager.

One FAISS index per account, stored as .faiss files on disk.
Each entry is an embedding vector + metadata (original tweet text).
"""

import os
import json
import numpy as np
import faiss
from typing import Optional
from app.config import EMBEDDING_DIM


class FaissIndexManager:
    """Manages a single FAISS index for one account."""

    def __init__(self, account: str, indices_dir: str, dim: int = EMBEDDING_DIM):
        self.account = account
        self.indices_dir = indices_dir
        self.dim = dim
        self.index_path = os.path.join(indices_dir, f"{account}.faiss")
        self.meta_path = os.path.join(indices_dir, f"{account}_meta.json")

        os.makedirs(indices_dir, exist_ok=True)

        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            self.metadata = self._load_metadata()
        else:
            self.index = faiss.IndexFlatL2(dim)
            self.metadata = []

    def index_exists(self) -> bool:
        return os.path.exists(self.index_path)

    def add(self, embedding: list[float], text: str) -> None:
        """Add a single embedding + text to the index."""
        vec = np.array([embedding], dtype=np.float32)
        self.index.add(vec)
        self.metadata.append({"text": text, "id": len(self.metadata)})

    def add_batch(self, embeddings: list[list[float]], texts: list[str]) -> None:
        """Add multiple embeddings and texts."""
        if not embeddings:
            return
        vecs = np.array(embeddings, dtype=np.float32)
        self.index.add(vecs)
        for i, text in enumerate(texts):
            self.metadata.append({"text": text, "id": len(self.metadata)})

    def query(
        self, text_or_embedding: str | list[float], k: int = 5
    ) -> tuple[float, dict]:
        """
        Query the index with text or an embedding vector.
        Returns (similarity_score, details).
        """
        from app.models.fanar import FanarClient

        if isinstance(text_or_embedding, str):
            fanar = FanarClient()
            query_vec = np.array([fanar.embed(text_or_embedding)], dtype=np.float32)
        else:
            query_vec = np.array([text_or_embedding], dtype=np.float32)

        if self.index.ntotal == 0:
            return 0.5, {"note": "Empty index"}

        distances, indices = self.index.search(query_vec, min(k, self.index.ntotal))

        # Convert L2 distance to similarity score (0-1)
        avg_dist = float(np.mean(distances[0]))
        similarity = max(0.0, min(1.0, 1.0 / (1.0 + avg_dist)))

        neighbors = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata) and idx >= 0:
                neighbors.append({
                    "text": self.metadata[idx]["text"][:100],
                    "distance": float(distances[0][i]),
                })

        details = {
            "index_size": self.index.ntotal,
            "nearest_neighbors": neighbors,
            "avg_distance": float(avg_dist),
        }
        return similarity, details

    def save(self) -> None:
        """Persist index and metadata to disk."""
        faiss.write_index(self.index, self.index_path)
        self._save_metadata()

    def _load_metadata(self) -> list[dict]:
        if not os.path.exists(self.meta_path):
            return []
        with open(self.meta_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_metadata(self) -> None:
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    @property
    def size(self) -> int:
        return self.index.ntotal
