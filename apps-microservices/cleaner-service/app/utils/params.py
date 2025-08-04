from app.utils.router.tags import RouterTags as Tags

from app.router.cleaner.cleaner import router as CleanerRouter
from app.router.embedding.embedding import router as EmbeddingRouter

params = [
    [
        CleanerRouter,
        f"/cleaner",
        Tags.cleaner,
        True
    ]
]
