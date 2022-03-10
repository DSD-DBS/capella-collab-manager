from fastapi import APIRouter

router = APIRouter()


@router.post("/", status_code=404)
def add_repository():
    return {}


@router.get("/")
def get_repositories():
    return [{"name": "test1", "name": "test2"}]
