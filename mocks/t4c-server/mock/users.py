from fastapi import APIRouter

router = APIRouter()


@router.post("/", status_code=404)
def add_user():
    return {}


@router.delete("/{userName}")
def remove_user():
    return {}


@router.put("/{userName}")
def update_user():
    return {}
