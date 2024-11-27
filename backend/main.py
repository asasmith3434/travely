from fastapi import FastAPI
from flights import router as flights_router  # Adjust import if `flights.py` is in a different folder

app = FastAPI()

# Include the flights router
app.include_router(flights_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Travel Visualizer API"}