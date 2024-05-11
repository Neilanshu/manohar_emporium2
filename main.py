from fastapi import FastAPI, HTTPException, Request, Form
from jsonschema import ValidationError
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pywhatkit
import time
from datetime import datetime
import pandas as pd
from datetime import datetime, timedelta
import time

# Create FastAPI instance
app = FastAPI()

# Database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    mobile_number = Column(String, index=True)
    whatsapp_number = Column(String, index=True)
    email = Column(String, index=True)
    locality = Column(String, index=True)
    classification = Column(String, index=True)

# Create database tables
Base.metadata.create_all(bind=engine)

# Pydantic model for request body
class UserData(BaseModel):
    name: str
    mobile_number: str
    whatsapp_number: str
    email: str
    locality: str
    classification: str = None

# Function to send WhatsApp message after 1 minute
def send_whatsapp_message(phone_number, message):
    current_time = datetime.now()
    send_time = current_time + timedelta(minutes=2)
    hour = send_time.hour
    minute = send_time.minute
    # time.sleep(60)
    pywhatkit.sendwhatmsg(phone_number, message, hour, minute)

# Endpoint to submit user data
@app.post("/submit_user_data/")
async def submit_user_data(
    name: str = Form(...),
    mobile_number: str = Form(...),
    whatsapp_number: str = Form(...),
    email: str = Form(...),
    locality: str = Form(...),
):
    db = SessionLocal()
    try:
        user_data = UserData(name=name, mobile_number=mobile_number, whatsapp_number=whatsapp_number, email=email, locality=locality)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    data = user_data.dict()
    sql_query = text(
        """
        INSERT INTO users (name, mobile_number, whatsapp_number, email, locality, classification) 
        VALUES (:name, :mobile_number, :whatsapp_number, :email, :locality, :classification)
    """
    )
    db.execute(sql_query, data)
    db.commit()

    return {"message": "User data submitted successfully!"}

# Endpoint to classify users
@app.post("/classify_users/")
async def classify_users():
    db = SessionLocal()
    classification_options = ['A', 'B', 'C']
    users = db.query(User).all()
    for index, user in enumerate(users):
        user.classification = classification_options[index]
    db.commit()
    return {"message": "User classification updated successfully!"}

# Endpoint to send WhatsApp messages
@app.post("/send_whatsapp_message/")
async def send_whatsapp_message_endpoint():
    db = SessionLocal()
    users = db.query(User).filter(User.whatsapp_number != None).all()
    for user in users:
        message = f"Hello {user.name}, thank you for being our customer! We have classified you as Class {user.classification}."
        send_whatsapp_message(user.whatsapp_number, message)
    return {"message": "WhatsApp messages sent successfully!"}

# Home page
@app.get("/")
async def home():
    return {"message": "Welcome to the homepage!"}
