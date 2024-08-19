from fastapi import APIRouter

router = APIRouter(prefix="", tags=["other_routes"])

@router.get("/")
async def index():
    return {"message": "Site is working"}