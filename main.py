from fastapi import FastAPI, HTTPException, Body
from firebase_admin import firestore
import firebase_admin
from firebase_admin import credentials

app = FastAPI()

cred = credentials.Certificate("user-d5c39-firebase-adminsdk-oo6ye-8ea5b57c2b.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Endpoint to create a user
@app.post("/add_users", status_code=201)
async def create_user(user_detail: dict = Body(...)):
    # Create a new document in 'users' collection with auto-generated ID
    doc_ref = db.collection('users').document()
    doc_ref.set(user_detail)  # Store user data in Firestore
    return {"message": "User created successfully", "user_id": doc_ref.id, "userdetail": user_detail}

# Endpoint to get all users
@app.get("/get_users", response_model=list[dict])
async def get_users():
    users = []
    for doc in db.collection('users').stream():
        users.append(doc.to_dict())
    return users

# Endpoint to get user by ID
@app.get("/get_user/{user_id}", response_model=dict)
async def get_user(user_id: str):
    doc_ref = db.collection('users').document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        raise HTTPException(status_code=404, detail="User not found")

# Endpoint to update user by ID
@app.patch("/update_user/{user_id}", response_model=dict)
async def update_user(user_id: str, user_detail: dict = Body(...)):
    doc_ref = db.collection('users').document(user_id)
    doc_ref.update(user_detail)
    return {"message": "User updated successfully", "user_id": user_id, "userdetail": user_detail}

# Endpoint to delete user by ID
@app.delete("/delete_user/{user_id}", response_model=dict)
async def delete_user(user_id: str):
    doc_ref = db.collection('users').document(user_id)
    doc_ref.delete()
    return {"message": "User deleted successfully"}
