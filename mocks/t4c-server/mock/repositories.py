from fastapi import APIRouter

router = APIRouter()


@router.post("/")
def add_repository():
    return {}


@router.get("/")
def get_repositories():
    return [{"name": "test1", "name": "test2"}]
