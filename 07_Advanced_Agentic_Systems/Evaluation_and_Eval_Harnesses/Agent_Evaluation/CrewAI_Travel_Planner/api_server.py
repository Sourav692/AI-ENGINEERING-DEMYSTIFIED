from fastapi import FastAPI
from pydantic import BaseModel
from TripCrew import TripCrew
import uvicorn

app = FastAPI()

class TripRequest(BaseModel):
    origin: str
    city: str
    customer_interest_topic: str
    date_range: str

@app.post("/plan_trip/")
def plan_trip(request: TripRequest):
    trip_crew = TripCrew(
        origin=request.origin,
        city=request.city,
        customer_interest_topic=request.customer_interest_topic,
        date_range=request.date_range
    )
    result = trip_crew.run()
    return {"trip_plan": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)