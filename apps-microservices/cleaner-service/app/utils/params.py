from app.utils.router.tags import RouterTags as Tags

from app.router.cleaner.cleaner import router as CleanerRouter

params = [
    [
        CleanerRouter,
        f"/cleaner",
        Tags.cleaner,
        True
    ]
]
