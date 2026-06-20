"""Embedding utilities for building FAISS indices."""

import numpy as np
from app.models.fanar import FanarClient
from app.db.faiss_index import FaissIndexManager


def build_account_index(
    account: str,
    tweets: list[dict],
    indices_dir: str,
    batch_size: int = 10,
) -> FaissIndexManager:
    """Build a FAISS index for an account from its tweets."""
    fanar = FanarClient()
    manager = FaissIndexManager(account, indices_dir)

    all_embeddings = []
    all_texts = []

    for i, tweet in enumerate(tweets):
        content = tweet.get("content", "")
        if not content:
            continue

        embedding = fanar.embed(content)
        all_embeddings.append(embedding)
        all_texts.append(content)

        if len(all_embeddings) >= batch_size:
            manager.add_batch(all_embeddings, all_texts)
            all_embeddings = []
            all_texts = []

    if all_embeddings:
        manager.add_batch(all_embeddings, all_texts)

    manager.save()
    return manager
