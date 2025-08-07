from app.utils.router.tags import RouterTags as Tags

from app.router.Milvus.crud_mivlus import router as CrudRouter

params = [
    [
        CrudRouter,
        f"/milvus",
        Tags.milvus,
        True
    ]
]
