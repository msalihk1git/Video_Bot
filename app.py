from flask import Flask, render_template, request, jsonify
import cloudinary
from cloudinary.uploader import upload as cloudinary_upload
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import requests
import random
import os

# Define possible prizes globally
possible_prizes = ["10% OFF ON FOOTWEAR", "20% OFFER ON JEANS", "50% OFFER ON INNERWEAR", "75% OFFER ON TOPWEAR", "25% OFF ON TELEVISION", "GIFT CARD", "45% OFFER ON TV"]

app = Flask(__name__)

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET")
)

# Cloudinary URL for the input image
input_image_url = 'https://res.cloudinary.com/dnyqripva/image/upload/v1708519385/input_video/Your_paragraph_text_1_gdhr9u.jpg'

def add_text_to_image(image, text, max_width, max_height, text_position, font_scale=1.0):
    # Convert the image to an OpenCV format (numpy array)
    frame = np.array(image)

    font = cv2.FONT_HERSHEY_DUPLEX
    font_thickness = 5
    font_color = (255, 255, 255)

    # Get the width and height of the text bounding box
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, font_thickness)

    # Calculate the position based on the specified text position
    position_x, position_y = text_position
    position_x = int(position_x - text_width / 2)
    position_y = int(position_y + text_height / 2)

    # Add text to the image with the calculated font size and position
    cv2.putText(frame, text, (position_x, position_y), font, font_scale, font_color, font_thickness)

    # Convert the modified frame back to PIL Image format
    result_image = Image.fromarray(frame)
    return result_image

def calculate_font_scale(text, max_width, max_height, font, font_thickness):
    # Initialize font scale
    initial_font_scale = 9.0  # You can adjust this initial value as needed

    # Get the width and height of the text bounding box with the initial font scale
    (text_width, text_height), _ = cv2.getTextSize(text, font, initial_font_scale, font_thickness)

    # Calculate font scales for width and height
    width_font_scale = max_width / text_width
    height_font_scale = max_height / text_height

    # Use the minimum of the two font scales to ensure both width and height fit within the specified area
    font_scale = min(initial_font_scale * width_font_scale, initial_font_scale * height_font_scale)

    return font_scale

@app.route('/')
def index():
    return render_template('index.html')

# @app.route('/result')
# def result():
#     return render_template('result.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    try:
        # Retrieve user name from the submitted form
        user_name = request.form.get('userName')

        # Validate user name
        if not user_name:
            return jsonify({"status": "error", "message": "Please enter your name"})

        # Fetch the input image from Cloudinary
        input_image = Image.open(BytesIO(requests.get(input_image_url).content))

        # Define the parameters for text placement
        max_width = 316
        max_height = 75
        text_position = (810, 864)  # Adjust this position as needed

        # Add user's name to the image with adjusted font scale
        user_font_scale = 1.5  # Adjust this value as needed
        result_image = add_text_to_image(input_image, user_name, max_width, max_height, text_position, font_scale=user_font_scale)

        # Add random prize text below user's name
        prize_text = f"You've won a {random.choice(possible_prizes)}"
        prize_text_position = (text_position[0], text_position[1] + max_height + 20)  # Adjust vertical position as needed

        # Increase the font scale for larger text
        prize_font_scale = 1.5  # Adjust this value as needed
        result_image = add_text_to_image(result_image, prize_text, max_width, max_height, prize_text_position, font_scale=prize_font_scale)

        # Save the modified image to a BytesIO object
        output_image_bytes = BytesIO()
        result_image.save(output_image_bytes, format="JPEG")
        output_image_bytes.seek(0)

        # Upload the modified image to Cloudinary
        cloudinary_response = cloudinary_upload(output_image_bytes, resource_type="image", folder="output_images")
        cloudinary_url = cloudinary_response['secure_url']

        return jsonify({"status": "success", "message": "Image generation completed", "image_path": cloudinary_url})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)