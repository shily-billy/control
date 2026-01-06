from fastapi import APIRouter

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_stats():
    return {
        "total_sales": 0,
        "total_revenue": 0,
        "total_commission": 0,
        "active_products": 0
    }

@router.get("/sales-by-platform")
async def get_sales_by_platform():
    return {"platforms": []}