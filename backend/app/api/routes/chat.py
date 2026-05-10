from fastapi import APIRouter

router = APIRouter()

@router.post("/chat")
async def send_answer(
    questrion: str
):
    ...