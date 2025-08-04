from app.utils.router.tags import RouterTags as Tags

from app.router.embedding.embedding import router as EmbeddingRouter

params = [
    [
        EmbeddingRouter,
        f"/embedding",
        Tags.embedding,
        True
    ]
]
