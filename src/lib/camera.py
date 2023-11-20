import requests
from requests.auth import HTTPDigestAuth
from PIL import Image
from io import BytesIO

IP = '192.168.1.64'
URL = "http://admin:heslo123456@192.168.1.64/ISAPI/Streaming/channels/1/picture"


class Camera:


    def __init__(self):
        pass

def download_and_show():

    try:
        response = requests.get(URL, auth=HTTPDigestAuth('admin', 'heslo123456'))

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Read the image data from the response content
            image_data = BytesIO(response.content)

            # Open the image using PIL (Python Imaging Library)
            img = Image.open(image_data)

            # Display the image
            img.show()
        else:
            print(f"Failed to retrieve image. Status code: {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    download_and_show()

