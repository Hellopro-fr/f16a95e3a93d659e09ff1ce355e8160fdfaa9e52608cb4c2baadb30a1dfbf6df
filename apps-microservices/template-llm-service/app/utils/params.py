from app.utils.router.tags import RouterTags as Tags
from app.routers.qualifier_router import router as QualifierRouter

params = [
    [QualifierRouter, "/qualifier", Tags.qualifier, True]
]
