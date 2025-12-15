import io
import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.security import APIKeyHeader
from uuid import uuid4
from dotenv import load_dotenv
import requests
from PIL import Image

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
FOTOR_API_KEY = os.getenv("FOTOR_API_KEY")  # Fotor API Key
API_KEY = os.getenv("API_KEY")  # FastAPI authentication key

# FastAPI application setup
app = FastAPI(
    title="Avatar Generator API",
    description="This API generates avatars from images by uploading them and processes the images using the Fotor API.",
    version="1.0.0"
)

# API Key security setup for FastAPI authentication
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=True)

# Helper function to validate the API key
def validate_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

# Ensure the 'avatars' directory exists
if not os.path.exists('avatars'):
    os.makedirs('avatars')

# Function to communicate with Fotor API for image processing
def process_image_with_fotor(image: Image.Image) -> bytes:
    """
    Sends the image to the Fotor API for processing (e.g., avatar generation, enhancement).
    """
    # Convert the image to a byte array to send to Fotor API
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # Fotor API endpoint for image processing (adjust if needed)
    FOTOR_API_URL = "https://api.fotor.com/v1/avataaars/avatar"  # Example endpoint

    # Headers for the Fotor API request
    headers = {
        "Authorization": f"Bearer {FOTOR_API_KEY}",
        "Content-Type": "multipart/form-data"  # Ensure this is correct for Fotor's API
    }

    # Sending the image to Fotor API (adjust the form data if required by the API)
    files = {
        "image": ("avatar.png", img_byte_arr, "image/png")
    }

    # Make the request to Fotor API for image processing
    response = requests.post(FOTOR_API_URL, headers=headers, files=files)

    if response.status_code == 200:
        avatar_data = response.content  # The processed avatar data (image)
        return avatar_data
    else:
        # Log the error or return a message for easier debugging
        raise HTTPException(status_code=500, detail=f"Error processing image with Fotor: {response.text}")

# Function to generate an avatar (using Fotor API)
@app.post("/generate-avatar/", tags=["Avatar Generation"])
async def create_avatar(file: UploadFile = File(...), api_key: str = Depends(validate_api_key)):
    """
    Upload an image and send it to the Fotor API to generate a circular avatar.
    The image will be processed by the Fotor API to generate the avatar.
    """
    # Check if the uploaded file is an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image.")

    try:
        # Read the uploaded image
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))

        # Send the image to Fotor for processing and get the avatar
        avatar_data = process_image_with_fotor(image)

        # Save the avatar (if it's in binary form, save it as a PNG)
        avatar_path = f'avatars/{str(uuid4())}.png'
        with open(avatar_path, 'wb') as f:
            f.write(avatar_data)

        # Return the generated avatar (PNG file)
        return FileResponse(avatar_path, media_type='image/png')

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
