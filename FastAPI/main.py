from fastapi import FastAPI, HTTPException, File, UploadFile,Form
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from contextlib import asynccontextmanager
from bson import ObjectId
import os
import aiofiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


origins = [
    "http://localhost:5173",
]




# MongoDB configuration
MONGO_URI = "mongodb+srv://aj123:aj123@shoppify.fsyemvp.mongodb.net/"
DATABASE_NAME = "db_example"
UPLOAD_DIR = "uploads"  # Directory to save uploaded files


# Utility function to save the file
async def save_file(file: UploadFile, upload_dir: str) -> str:
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    async with aiofiles.open(file_path, "wb") as out_file:
        while content := await file.read(1024):
            await out_file.write(content)
    return file_path


# FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    mongo_client = AsyncIOMotorClient(MONGO_URI)
    db = mongo_client[DATABASE_NAME]
    app.state.db = db  # Attach the database to app.state
    print("Connected to MongoDB")
    yield
    # Shutdown logic
    await mongo_client.close()
    print("MongoDB connection closed")

app = FastAPI(lifespan=lifespan)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Example data model
class Item(BaseModel):
    name: str
    description: str
    price: float

# Example route to create an item
@app.post("/items/")
async def create_item(item: Item):
    item_data = item.model_dump()  # Use model_dump instead of dict
    result = await app.state.db["items"].insert_one(item_data)
    return {"id": str(result.inserted_id), "message": "Item created successfully"}

# Example route to get an item by ID
@app.get("/items/{item_id}")
async def read_item(item_id: str):
    item = await app.state.db["items"].find_one({"_id": ObjectId(item_id)})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item["_id"] = str(item["_id"])  # Convert ObjectId to string for response
    return item


# Example data model
class User(BaseModel):
    name: str
    email: str
    photo: str



@app.post("/users/")
async def create_user(
    name: str = Form(...),
    email: str = Form(...),
    photo: UploadFile = File(...),
):
    try:
        # Save the file
        saved_filename = await save_file(photo, UPLOAD_DIR)
        file_url = f"http://127.0.0.1:8000/{saved_filename}"

        # Insert data into MongoDB
        user_data = {"name": name, "email": email, "photo": file_url}
        result = await app.state.db["users"].insert_one(user_data)

        return {
            "id": str(result.inserted_id),
            "message": "User created successfully",
            "file_path": file_url,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

