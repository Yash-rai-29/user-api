from fastapi import FastAPI, HTTPException, Body, Query
import boto3
import uuid
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# Initialize Boto3 session and DynamoDB resource
session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)
dynamodb = session.resource('dynamodb')

# Specify your DynamoDB table name
table_name = 'users'  # Replace with your DynamoDB table name
table = dynamodb.Table(table_name)

# Check API is running
@app.get("/")
async def api():
    return "API is running successfully! Try '/get_users' to fetch all users"

# Endpoint to create a user
@app.post("/add_users", status_code=201)
async def create_user(user_detail: dict = Body(...)):
    # Generate a unique userid using UUID
    user_id = str(uuid.uuid4())  # Convert UUID to string
    
    # Add the generated userid to user_detail
    user_detail['userid'] = user_id
    
    # Perform PutItem operation in DynamoDB
    response = table.put_item(Item=user_detail)
    
    # Return response
    return {"message": "User created successfully", "user_id": user_id, "userdetail": user_detail}

# Endpoint to get all users
@app.get("/get_users", response_model=list[dict])
async def get_users():
    try:
        response = table.scan()
        return response['Items']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to get user by ID
@app.get("/get_user/{user_id}", response_model=dict)
async def get_user(user_id: str):
    try:
        response = table.get_item(Key={'userid': user_id})
        item = response.get('Item')
        if item:
            return item
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to update user by ID
@app.patch("/update_user/{user_id}", response_model=dict)
async def update_user(user_id: str, user_detail: dict = Body(...)):
    try:
        # Retrieve existing user data
        existing_user = await get_user(user_id)
        
        # Prepare UpdateExpression and ExpressionAttributeValues
        update_expression_parts = []
        expression_attribute_values = {}
        
        for key, value in user_detail.items():
            if key in existing_user:
                update_expression_parts.append(f"{key} = :{key}")
                expression_attribute_values[f":{key}"] = value
            else:
                raise HTTPException(status_code=400, detail=f"Attribute '{key}' not found in existing user details")
        
        # Build UpdateExpression
        update_expression = "SET " + ", ".join(update_expression_parts)
        
        # Update user detail in DynamoDB
        response = table.update_item(
            Key={'userid': user_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues='ALL_NEW'  # Return updated item
        )
        
        return response.get('Attributes', {})
    
    except HTTPException:
        raise  # Re-raise HTTPException to maintain proper error handling and status code
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to delete user by ID
@app.delete("/delete_user/{user_id}", response_model=dict)
async def delete_user(user_id: str):
    try:
        # Delete user from DynamoDB
        response = table.delete_item(Key={'userid': user_id})
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
