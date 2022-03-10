from fastapi import APIRouter

router = APIRouter()


@router.post("/")
def add_user():
    return {}


@router.delete("/{userName}")
def remove_user():
    return {}


@router.put("/{userName}")
def update_user():
    return {}
