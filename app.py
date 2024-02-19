# from flask import Flask, render_template, request, jsonify, send_from_directory
# from flask_socketio import SocketIO
# from flask_cors import CORS  # Import CORS from the flask_cors extension
# import cv2
# import numpy as np
# import random
# import os

# app = Flask(__name__)
# CORS(app)  # Add this line to enable CORS
# socketio = SocketIO(app)

# # Specified video path
# # video_path = r"C:\Users\msali\Program_Files\PersonalisedVideoNew\sample_video2.mp4"
# video_path = "sample_video2.mp4"

# def add_text_to_frame(frame, text, position, max_width, max_height, font_scale=1.0):
#     font = cv2.FONT_HERSHEY_DUPLEX
#     font_thickness = 2
#     font_color = (0, 0, 0)

#     # Get the width and height of the text bounding box
#     (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, font_thickness)

#     # Calculate the position to center the text within the specified area
#     position_x, position_y = position
#     position_x = int(position_x + (max_width - text_width) / 2)
#     position_y = int(position_y + (max_height + text_height) / 2)

#     # Add text to the frame with the calculated font size and position
#     cv2.putText(frame, text, (position_x, position_y), font, font_scale, font_color, font_thickness)
#     return frame


# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp4', 'avi', 'mov'}

# @socketio.on('connect')
# def handle_connect():
#     print('Client connected')

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/result')
# def result():
#     return render_template('result.html')

# @app.route('/process_video', methods=['POST'])
# def process_video():
#     try:
#         # Check if the request is JSON
#         if request.is_json:
#             data = request.get_json()
#         else:
#             # If not JSON, try to get data from form
#             data = request.form.to_dict()

#         user_name = data.get('userName')
#         sender_phone_number = data.get('senderPhoneNumber')

#         # Validate user name
#         if not user_name:
#             return jsonify({"status": "error", "message": "Please enter your name"})

#         # Validate file type
#         if os.path.isfile(video_path) and allowed_file(video_path):
#             cap = cv2.VideoCapture(video_path)
#             fps = cap.get(cv2.CAP_PROP_FPS)

#             modified_frames = []

#             possible_prizes = ["10% OFF ON FOOTWEAR", "20%OFFER ON JEANS", "50% OFFER ON INNERWEAR", "75% OFFER ON TOPWEAR", "25% OFF ON TELEVISION", "GIFT CARD", "45% OFFER ON TV"]
#             random_prize = random.choice(possible_prizes)

#             while True:
#                 ret, frame = cap.read()

#                 if not ret:
#                     break

#                 start_time = 3
#                 stop_time = 9
#                 current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

#                 if start_time <= current_time <= stop_time:
#                     user_text_combined = f"{user_name}"
#                     prize_text_combined = f"You've won a {random_prize}"

#                     max_width = 316
#                     max_height = 75

#                     frame = add_text_to_frame(frame, user_text_combined, (271, 864), max_width, max_height)
#                     frame = add_text_to_frame(frame, prize_text_combined, (271 , 899), max_width, max_height)

#                 modified_frames.append(frame)

#             cap.release()

#             if modified_frames:
#                 output_video_path = "static/output_video.mp4"
#                 out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (modified_frames[0].shape[1], modified_frames[0].shape[0]))

#                 for modified_frame in modified_frames:
#                     out.write(modified_frame)

#                 out.release()

#                 # Emit a socket event to inform the WhatsApp client about the generated video
#                 socketio.emit('video_generated', {'video_path': output_video_path, 'phone_number': sender_phone_number})    

#                 return jsonify({"status": "success", "message": "Video generation completed", "video_path": output_video_path})
#             else:
#                 return jsonify({"status": "error", "message": "No frames to process"})

#         return jsonify({"status": "error", "message": "Invalid file type. Please provide a valid video."})

#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)})

# @app.route('/static/<filename>')
# def serve_video(filename):
#     return send_from_directory('static', filename)

# if __name__ == '__main__':
#     socketio.run(app, debug=True)

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS  # Import CORS from the flask_cors extension
import cloudinary
from cloudinary import config as cloudinary_config, uploader
import os
from dotenv import load_dotenv 

load_dotenv()


# Configure Cloudinary
cloudinary_config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

import cv2
import numpy as np
import random
import os

app = Flask(__name__)
CORS(app)  # Add this line to enable CORS
socketio = SocketIO(app)

# Specified video path
video_path = "sample_video2.mp4"

def add_text_to_frame(frame, text, position, max_width, max_height, font_scale=1.0):
    font = cv2.FONT_HERSHEY_DUPLEX
    font_thickness = 2
    font_color = (0, 0, 0)

    # Get the width and height of the text bounding box
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, font_thickness)

    # Calculate the position to center the text within the specified area
    position_x, position_y = position
    position_x = int(position_x + (max_width - text_width) / 2)
    position_y = int(position_y + (max_height + text_height) / 2)

    # Add text to the frame with the calculated font size and position
    cv2.putText(frame, text, (position_x, position_y), font, font_scale, font_color, font_thickness)
    return frame


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp4', 'avi', 'mov'}

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result')
def result():
    return render_template('result.html')

@app.route('/process_video', methods=['POST'])
def process_video():
    try:
        # Check if the request is JSON
        if request.is_json:
            data = request.get_json()
        else:
            # If not JSON, try to get data from form
            data = request.form.to_dict()

        user_name = data.get('userName')
        sender_phone_number = data.get('senderPhoneNumber')

        # Validate user name
        if not user_name:
            return jsonify({"status": "error", "message": "Please enter your name"})

        # Validate file type
        if os.path.isfile(video_path) and allowed_file(video_path):
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)

            modified_frames = []

            possible_prizes = ["10% OFF ON FOOTWEAR", "20%OFFER ON JEANS", "50% OFFER ON INNERWEAR", "75% OFFER ON TOPWEAR", "25% OFF ON TELEVISION", "GIFT CARD", "45% OFFER ON TV"]
            random_prize = random.choice(possible_prizes)

            while True:
                ret, frame = cap.read()

                if not ret:
                    break

                start_time = 3
                stop_time = 9
                current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

                if start_time <= current_time <= stop_time:
                    user_text_combined = f"{user_name}"
                    prize_text_combined = f"You've won a {random_prize}"

                    max_width = 316
                    max_height = 75

                    frame = add_text_to_frame(frame, user_text_combined, (271, 864), max_width, max_height)
                    frame = add_text_to_frame(frame, prize_text_combined, (271 , 899), max_width, max_height)

                modified_frames.append(frame)

            cap.release()

            if modified_frames:
                output_video_path = "static/output_video.mp4"
            out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (modified_frames[0].shape[1], modified_frames[0].shape[0]))

            for modified_frame in modified_frames:
                out.write(modified_frame)

            out.release()

            # Upload video to Cloudinary
            cloudinary_response = uploader.upload(output_video_path, resource_type="video")

            # Extract Cloudinary URL from the response
            cloudinary_url = cloudinary_response['secure_url']

            # Emit a socket event to inform the WhatsApp client about the generated video
            socketio.emit('video_generated', {'video_path': cloudinary_url, 'phone_number': sender_phone_number})    

            return jsonify({"status": "success", "message": "Video generation completed", "video_path": cloudinary_url})
        else:   
            return jsonify({"status": "error", "message": "No frames to process"})

        return jsonify({"status": "error", "message": "Invalid file type. Please provide a valid video."})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/static/<filename>')
def serve_video(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    socketio.run(app, debug=True)