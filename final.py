from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from tortoise import Tortoise, fields
from tortoise.models import Model
from tortoise.contrib.fastapi import register_tortoise
import pywhatkit
from datetime import datetime, timedelta

# Create FastAPI instance
app = FastAPI()

# Initialize Tortoise ORM
Tortoise.init_models(["__main__"], "models")

# Define User model using Tortoise ORM
class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    mobile_number = fields.CharField(max_length=20)
    whatsapp_number = fields.CharField(max_length=20)
    email = fields.CharField(max_length=255)
    locality = fields.CharField(max_length=255)
    classification = fields.CharField(max_length=1)

    class Meta:
        table = "users"

# Register Tortoise models with FastAPI
register_tortoise(
    app,
    db_url="sqlite://./Manohar.db",  # Use SQLite database
    modules={"models": ["__main__"]},
    generate_schemas=True,
)

# Function to send WhatsApp message after 2 minutes
def send_whatsapp_message(phone_number, message):
    current_time = datetime.now()
    send_time = current_time + timedelta(minutes=2)
    hour = send_time.hour
    minute = send_time.minute
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
    user = await User.create(
        name=name,
        mobile_number=mobile_number,
        whatsapp_number=whatsapp_number,
        email=email,
        locality=locality,
    )
    return {"message": "User data submitted successfully!", "user_id": user.id}

# Endpoint to classify users
@app.post("/classify_users/")
async def classify_users(user_id: int = Form(...), classification: str = Form(...)):
    user = await User.filter(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.classification = classification.upper()
    await user.save()
    return {"message": "User classification updated successfully!"}

# Endpoint to send WhatsApp messages
@app.post("/send_whatsapp_message/")
async def send_whatsapp_message_endpoint():
    users = await User.filter(whatsapp_number__not=None)
    for user in users:
        message = f"Hello {user.name}, thank you for being our customer! We have classified you as Class {user.classification}."
        send_whatsapp_message(user.whatsapp_number, message)
    return RedirectResponse(url="/", status_code=303)

# Home page with GUI
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
    <head>
        <title>User Data Submission</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f2f2f2;
            }
            .container {
                width: 600px;
                margin: 50px auto;
                background-color: #fff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            h1 {
                text-align: center;
            }
            form {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
            }
            input[type="text"], select {
                width: calc(100% - 22px);
                padding: 10px;
                margin-bottom: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            input[type="submit"] {
                width: 100%;
                padding: 10px 0;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            input[type="submit"]:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>User Data Submission</h1>
            <form id="user-form" action="/submit_user_data/" method="post">
                <label for="name">Name:</label>
                <input type="text" id="name" name="name" required><br>
                <label for="mobile_number">Mobile Number:</label>
                <input type="text" id="mobile_number" name="mobile_number" required><br>
                <label for="whatsapp_number">WhatsApp Number:</label>
                <input type="text" id="whatsapp_number" name="whatsapp_number" required><br>
                <label for="email">Email:</label>
                <input type="text" id="email" name="email" required><br>
                <label for="locality">Locality:</label>
                <input type="text" id="locality" name="locality" required><br>
                <input type="submit" value="Submit">
            </form>
            <div id="classification-container" style="display: none;">
                <form id="classification-form" action="/classify_users/" method="post">
                    <input type="hidden" id="user_id" name="user_id">
                    <label for="classification">Classify User (A, B, C):</label>
                    <input type="text" id="classification" name="classification" required><br>
                    <input type="submit" value="Classify">
                </form>
            </div>
            <div id="send-whatsapp-container" style="display: none;">
                <form action="/send_whatsapp_message/" method="post">
                    <input type="submit" value="Send WhatsApp Messages">
                </form>
            </div>
        </div>
        <script>
            const userForm = document.getElementById('user-form');
            const classificationContainer = document.getElementById('classification-container');
            const classificationForm = document.getElementById('classification-form');
            const userIdInput = document.getElementById('user_id');

            userForm.addEventListener('submit', async (event) => {
                event.preventDefault();
                const formData = new FormData(event.target);
                const response = await fetch('/submit_user_data/', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                userIdInput.value = data.user_id;
                classificationContainer.style.display = 'block';
            });

            classificationForm.addEventListener('submit', async (event) => {
                event.preventDefault();
                const formData = new FormData(event.target);
                await fetch('/classify_users/', {
                    method: 'POST',
                    body: formData
                });
                const sendWhatsAppContainer = document.getElementById('send-whatsapp-container');
                sendWhatsAppContainer.style.display = 'block';
            });
        </script>
    </body>
    </html>
    """
