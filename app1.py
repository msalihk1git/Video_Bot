from flask import Flask, request, jsonify, render_template
import cloudinary
from cloudinary.uploader import upload as cloudinary_upload
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import requests
import random
import os
import axios

app = Flask(__name__)

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET")
)

# Cloudinary URL for the input image
input_image_url = 'https://res.cloudinary.com/dnyqripva/image/upload/v1708519385/input_video/Your_paragraph_text_1_gdhr9u.jpg'

possible_prizes = ["10% OFF ON FOOTWEAR", "20% OFFER ON JEANS", "50% OFFER ON INNERWEAR", "75% OFFER ON TOPWEAR", "25% OFF ON TELEVISION", "GIFT CARD", "45% OFFER ON TV"]

# Store user chat sessions
chat_sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        body = request.json
        print(json.dumps(body, indent=2))

        if body.get("object"):
            changes = body.get("entry", [])[0].get("changes", [])
            if changes and changes[0].get("value", {}).get("messages"):
                handle_whatsapp_message(changes[0]["value"]["messages"][0])

        return jsonify({"status": "success"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

def handle_whatsapp_message(message):
    global phone_number_id
    global chat_sessions

    phone_number_id = message.get("metadata", {}).get("phone_number_id")
    user = message["from"]
    msg_body = message["text"]["body"]

    if not chat_sessions.get(user):
        initiate_chat(user)
    elif chat_sessions[user].get("waiting_for_name"):
        send_image_message(user, msg_body)
        chat_sessions[user]["interaction_completed"] = True
    elif chat_sessions[user].get("interaction_completed"):
        pass
    else:
        handle_user_message(user, msg_body)

def initiate_chat(user):
    sendMessage(user, "Pixelflames Technologies \n Enter your name?")
    chat_sessions[user] = {"waiting_for_name": True}

def send_image_message(user, name):
    if not chat_sessions[user].get("image_sent"):
        thank_you_message = f"Thank you, {name}, for sharing your name. Here is a gift for you"
        sendMessage(user, thank_you_message)

        image_url = "https://res.cloudinary.com/dgs55s8qh/image/upload/v1708520824/ibzudqsco1u3qacmvles.jpg"
        send_image(user, image_url)

        chat_sessions[user]["image_sent"] = True

def sendMessage(user, message):
    # Your WhatsApp message sending logic here
    pass

def send_image(user, image_url):
    # Your WhatsApp image sending logic here
    pass

def handle_user_message(user, message):
    # Your logic for handling user messages
    pass

@app.route('/process_image', methods=['POST'])
def process_image():
    try:
        user_name = request.form.get('userName')

        if not user_name:
            return jsonify({"status": "error", "message": "Please enter your name"})

        input_image = Image.open(BytesIO(requests.get(input_image_url).content))

        max_width = 316
        max_height = 75
        text_position = (810, 864)

        user_font_scale = 1.5
        result_image = add_text_to_image(input_image, user_name, max_width, max_height, text_position, font_scale=user_font_scale)

        prize_text = f"You've won a {random.choice(possible_prizes)}"
        prize_text_position = (text_position[0], text_position[1] + max_height + 20)
        prize_font_scale = 1.5
        result_image = add_text_to_image(result_image, prize_text, max_width, max_height, prize_text_position, font_scale=prize_font_scale)

        output_image_bytes = BytesIO()
        result_image.save(output_image_bytes, format="JPEG")
        output_image_bytes.seek(0)

        cloudinary_response = cloudinary_upload(output_image_bytes, resource_type="image", folder="output_images")
        cloudinary_url = cloudinary_response['secure_url']

        return jsonify({"status": "success", "message": "Image generation completed", "image_path": cloudinary_url})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

def add_text_to_image(image, text, max_width, max_height, text_position, font_scale=1.0):
    frame = np.array(image)

    font = cv2.FONT_HERSHEY_DUPLEX
    font_thickness = 5
    font_color = (255, 255, 255)

    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, font_thickness)

    position_x, position_y = text_position
    position_x = int(position_x - text_width / 2)
    position_y = int(position_y + text_height / 2)

    cv2.putText(frame, text, (position_x, position_y), font, font_scale, font_color, font_thickness)

    result_image = Image.fromarray(frame)
    return result_image

if __name__ == '__main__':
    app.run(debug=True)