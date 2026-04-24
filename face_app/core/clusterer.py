"""DBSCAN-based face clustering to group faces into identities.

Each cluster produced by DBSCAN maps to one :class:`~face_app.db.models.Person`.
Noise points (label == -1) are left unassigned and can be reviewed later.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import normalize


@dataclass
class ClusterResult:
    """Mapping from face DB id → cluster label (−1 means noise / unassigned)."""

    face_ids: list[int]
    labels: list[int]      # parallel to face_ids
    n_clusters: int        # number of unique identities found (excluding noise)


def cluster_embeddings(
    face_ids: list[int],
    embeddings: list[bytes],
    eps: float = 0.5,
    min_samples: int = 2,
) -> ClusterResult:
    """Cluster face embeddings with DBSCAN (cosine distance).

    Args:
        face_ids:   DB primary keys for each face (parallel to *embeddings*).
        embeddings: Raw embedding bytes — 128 × float32 per face.
        eps:        DBSCAN neighbourhood radius (cosine distance, 0–2).
        min_samples: Minimum cluster size; smaller clusters become noise.

    Returns:
        :class:`ClusterResult` with per-face cluster labels.
    """
    if not face_ids:
        return ClusterResult(face_ids=[], labels=[], n_clusters=0)

    if len(face_ids) != len(embeddings):
        raise ValueError("face_ids and embeddings must have the same length")

    # Decode and L2-normalise so Euclidean distance ≈ cosine distance.
    vecs = np.array(
        [np.frombuffer(e, dtype=np.float32) for e in embeddings], dtype=np.float32
    )
    vecs = normalize(vecs, norm="l2")

    db = DBSCAN(eps=eps, min_samples=min_samples, metric="euclidean", n_jobs=-1)
    labels: np.ndarray = db.fit_predict(vecs)

    n_clusters = int(np.max(labels)) + 1 if np.any(labels >= 0) else 0
    return ClusterResult(
        face_ids=list(face_ids),
        labels=labels.tolist(),
        n_clusters=n_clusters,
    )


def pick_representative_face(
    face_ids: list[int],
    embeddings: list[bytes],
) -> int:
    """Return the face id whose embedding is closest to the cluster centroid.

    Args:
        face_ids:   DB primary keys for the faces in a single cluster.
        embeddings: Corresponding embedding bytes (same order as *face_ids*).

    Returns:
        The face id of the most central face.
    """
    vecs = np.array(
        [np.frombuffer(e, dtype=np.float32) for e in embeddings], dtype=np.float32
    )
    centroid = vecs.mean(axis=0)
    dists = np.linalg.norm(vecs - centroid, axis=1)
    best_idx = int(np.argmin(dists))
    return face_ids[best_idx]
