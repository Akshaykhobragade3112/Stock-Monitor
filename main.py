from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from typing import List
from pydantic import BaseModel

app = FastAPI()
client = MongoClient('mongodb://localhost:27017/')
db = client['property_management']

class Property(BaseModel):
    name: str
    address: str
    city: str
    state: str

@app.post("/create_new_property")
async def create_new_property(property: Property):
    property_dict = property.dict()
    db.properties.insert_one(property_dict)
    return {"message": "Property created successfully", "property": property_dict}

@app.get("/fetch_property_details/{city}", response_model=List[Property])
async def fetch_property_details(city: str):
    properties = db.properties.find({"city": city})
    return [Property(**property) for property in properties]

@app.put("/update_property_details/{property_id}")
async def update_property_details(property_id: str, property: Property):
    result = db.properties.replace_one({"_id": ObjectId(property_id)}, property.dict())
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Property not found")
    return {"message": "Property updated successfully", "property": property.dict()}

# Non-mandatory APIs
@app.get("/find_cities_by_state/{state_id_or_name}", response_model=List[str])
async def find_cities_by_state(state_id_or_name: str):
    if state_id_or_name.isdigit():
        state_id = ObjectId(state_id_or_name)
        cities = db.properties.distinct("city", {"state": state_id})
    else:
        cities = db.properties.distinct("city", {"state": state_id_or_name})
    return cities

@app.get("/find_similar_properties/{property_id}", response_model=List[Property])
async def find_similar_properties(property_id: str):
    property_ = db.properties.find_one({"_id": ObjectId(property_id)})
    city = property_["city"]
    similar_properties = db.properties.find({"city": city})
    return [Property(**property) for property in similar_properties]