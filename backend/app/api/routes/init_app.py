from fastapi import APIRouter

router = APIRouter(prefix="/test", tags=["main"])

@router.get("/")
async def test_get():
    return {"message": "Ок"}


@router.post("/")
async def test_post():
    return {"message": "Ок"}