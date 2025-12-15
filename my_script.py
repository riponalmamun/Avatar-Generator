import requests

# URL of the FastAPI app
url = 'http://127.0.0.1:8000/random'

# Send a GET request to the FastAPI app to get the random avatar
response = requests.get(url)

# Check if the response is successful
if response.status_code == 200:
    # Save the avatar image to a local file (assuming the image is returned in PNG format)
    with open('random_avatar.png', 'wb') as file:
        file.write(response.content)
    print("Avatar saved as random_avatar.png")
else:
    print(f"Failed to get avatar. Status code: {response.status_code}")
