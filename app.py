# from flask import Flask, render_template, request, jsonify, send_from_directory
# from flask_socketio import SocketIO
# from flask_cors import CORS  # Import CORS from the flask_cors extension
# import cloudinary
# from cloudinary import config as cloudinary_config, uploader
# import os
# import cv2
# import numpy as np
# import random

# # Configure Cloudinary
# cloudinary.config(
#     cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
#     api_key=os.environ.get("CLOUDINARY_API_KEY"),
#     api_secret=os.environ.get("CLOUDINARY_API_SECRET")
# )


# app = Flask(__name__)
# CORS(app)  # Add this line to enable CORS
# socketio = SocketIO(app)

# # Specify video path
# video_path = 'https://res.cloudinary.com/dnyqripva/video/upload/v1708405239/output_video/displayed.mp4'

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
#     # Accept any file or Cloudinary URL
#     return True

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
#             user_name = data.get('userName')
#         else:
#             # If not JSON, assume form data
#             user_name = request.form.get('userName')

#         # Validate user name
#         if not user_name:
#             return jsonify({"status": "error", "message": "Please enter your name"})

#         cap = cv2.VideoCapture(video_path)
#         fps = cap.get(cv2.CAP_PROP_FPS)

#         # Specify the output video path
#         temp_output_path = 'temp_output.mp4'
#         out = cv2.VideoWriter(temp_output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (int(cap.get(3)), int(cap.get(4))))

#         start_time = 3
#         stop_time = 9

#         possible_prizes = ["10% OFF ON FOOTWEAR", "20%OFFER ON JEANS", "50% OFFER ON INNERWEAR", "75% OFFER ON TOPWEAR", "25% OFF ON TELEVISION", "GIFT CARD", "45% OFFER ON TV"]
#         random_prize = random.choice(possible_prizes)

#         while True:
#             ret, frame = cap.read()

#             if not ret:
#                 print("No more frames to process.")
#                 break

#             print("Processing frame...")

#             current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

#             if start_time <= current_time <= stop_time:
#                 user_text_combined = f"{user_name}"
#                 prize_text_combined = f"You've won a {random_prize}"

#                 max_width = 316
#                 max_height = 75

#                 frame = add_text_to_frame(frame, user_text_combined, (271, 864), max_width, max_height)
#                 frame = add_text_to_frame(frame, prize_text_combined, (271, 899), max_width, max_height)

#             # Write the modified frame directly to the output video
#             out.write(frame)

#         cap.release()
#         out.release()  # Release the VideoWriter

#         print("Number of frames processed.")

#         # Upload the output video file to Cloudinary
#         cloudinary_response = uploader.upload(temp_output_path, resource_type="video", folder="output_video")
#         cloudinary_url = cloudinary_response['secure_url']

#         # Remove the temporary video file
#         os.remove(temp_output_path)

#         # Emit a socket event to inform the client about the generated video
#         socketio.emit('video_generated', {'video_path': cloudinary_url})

#         return jsonify({"status": "success", "message": "Video generation completed", "video_path": cloudinary_url})

#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)})

from flask import Flask, render_template, request, jsonify
import cloudinary
from cloudinary.uploader import upload as cloudinary_upload
import cv2
import numpy as np
import random
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

cloudinary.config(
    cloud_name="dnyqripva",
    api_key="648727619819579",
    api_secret="8IMHMm-1S4bxZ09DylKyKNS7Zfk"
)

# Cloudinary URL for the input video
input_video_url = 'https://res.cloudinary.com/dnyqripva/video/upload/v1708424613/input_video/Copy_of_namith_ks_jkfvd1.mp4'

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
    # Accept any file or Cloudinary URL
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result')
def result():
    return render_template('result.html')

@app.route('/process_video', methods=['POST'])
def process_video():
    try:
        # Retrieve user name from the submitted form
        user_name = request.form.get('userName')

        # Validate user name
        if not user_name:
            return jsonify({"status": "error", "message": "Please enter your name"})

        # Fetch the input video from Cloudinary
        cap = cv2.VideoCapture(input_video_url)
        fps = cap.get(cv2.CAP_PROP_FPS)

        modified_frames = []
        possible_prizes = ["car", "bike", "washing machine", "flight ticket", "tour package", "cooker", "refrigerator"]
        random_prize = random.choice(possible_prizes)

        while True:
            ret, frame = cap.read()

            if not ret:
                break


            # Assuming a constant start and stop time for demonstration
            start_time = 3
            stop_time = 7
            current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

            if start_time <= current_time <= stop_time:
                user_text_combined = f"{user_name}"
                prize_text_combined = f"You've won a {random_prize}"

                # Assuming max_width and max_height are the dimensions of the specific area
                max_width = 316
                max_height = 75

                frame = add_text_to_frame(frame, user_text_combined, (271, 864), max_width, max_height)
                frame = add_text_to_frame(frame, prize_text_combined, (271, 899), max_width, max_height)

            modified_frames.append(frame)

        cap.release()

        if modified_frames:
            # Write the modified frames to a temporary video file
            temp_output_path = 'temp_output.mp4'
            out = cv2.VideoWriter(temp_output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (modified_frames[0].shape[1], modified_frames[0].shape[0]))
            for modified_frame in modified_frames:
                out.write(modified_frame)
            out.release()

            # Upload the temporary video file to Cloudinary
            cloudinary_response = cloudinary_upload(temp_output_path, resource_type="video", folder="output_video")
            cloudinary_url = cloudinary_response['secure_url']

            # Remove the temporary video file
            os.remove(temp_output_path)

            return jsonify({"status": "success", "message": "Video generation completed", "video_path": cloudinary_url})
        else:
            return jsonify({"status": "error", "message": "No frames to process"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)