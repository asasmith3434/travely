from fastapi import APIRouter

router = APIRouter()

@router.get("/flights")
async def get_flights(origin: str, destination: str):
    # Placeholder for external API integration
    return {"origin": origin, "destination": destination, "price": "$200"}
