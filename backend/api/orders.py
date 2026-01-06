from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_orders():
    return {"message": "Orders API - Coming Soon"}

@router.post("/")
async def create_order():
    return {"message": "Create order - Coming Soon"}