# import pyimgur

# def Upload_image(path ,title = "人員"):
#     CLIENT_ID = "ab4121c43965a5b"
#     im = pyimgur.Imgur(CLIENT_ID)
#     uploaded_image = im.upload_image(path, title=title)
#     return uploaded_image.link

import json , requests
import base64
def Upload_image(path):
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    url = "https://api.imgur.com/3/image"
    headers = {
        "Authorization": "Client-ID ab4121c43965a5b"  # 確保加上 "Client-ID "
    }
    app_token = "882e673ad2be3d9733f0800c1d22a2c4abb18e9d"
    response = requests.post(
        url,
        headers=headers,
        data={
            "image": encoded_string,
            "type": "base64",
            "name": "bear1.jpg",
            "title": "ehappy_bear1"
        }
    )

    data = response.json()["data"]
    link = data['link']
    if not link.endswith('.jpg'):
        link = f"https://i.imgur.com/{data['id']}.jpg"

    print("JPG 連結：", link)
    return link

# Upload_image("static/media/faceID_image/下載_1_LEz3CUg.jpg")