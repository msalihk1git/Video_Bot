from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS  # Import CORS from the flask_cors extension
import cv2
import numpy as np
import random
import os

app = Flask(__name__)
CORS(app)  # Add this line to enable CORS
socketio = SocketIO(app)

# Specified video path
# video_path = r"C:\Users\msali\Program_Files\PersonalisedVideoNew\sample_video2.mp4"
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

                # Emit a socket event to inform the WhatsApp client about the generated video
                socketio.emit('video_generated', {'video_path': output_video_path, 'phone_number': sender_phone_number})    

                return jsonify({"status": "success", "message": "Video generation completed", "video_path": output_video_path})
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

# from flask import Flask, render_template, request, jsonify, send_file
# from flask_socketio import SocketIO
# from flask_cors import CORS
# import cv2
# import numpy as np
# import random
# import os
# import tempfile
# import shutil

# app = Flask(__name__)
# CORS(app)
# socketio = SocketIO(app)

# video_path = "sample_video2.mp4"

# def add_text_to_frame(frame, text, position, max_width, max_height, font_scale=1.0):
#     font = cv2.FONT_HERSHEY_DUPLEX
#     font_thickness = 2
#     font_color = (0, 0, 0)

#     (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, font_thickness)

#     position_x, position_y = position
#     position_x = int(position_x + (max_width - text_width) / 2)
#     position_y = int(position_y + (max_height + text_height) / 2)

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


# @app.route('/process_video', methods=['POST'])
# def process_video():
#     try:
#         if request.is_json:
#             data = request.get_json()
#         else:
#             data = request.form.to_dict()

#         user_name = data.get('userName')
#         sender_phone_number = data.get('senderPhoneNumber')

#         if not user_name:
#             return jsonify({"status": "error", "message": "Please enter your name"})

#         if os.path.isfile(video_path) and allowed_file(video_path):
#             cap = cv2.VideoCapture(video_path)
#             fps = cap.get(cv2.CAP_PROP_FPS)

#             modified_frames = []

#             possible_prizes = ["10% OFF ON FOOTWEAR", "20%OFFER ON JEANS", "50% OFFER ON INNERWEAR", "75% OFFER ON TOPWEAR", "25% OFF ON TELEVISION", "GIFT CARD", "45% OFFER ON TV"]
#             random_prize = random.choice(possible_prizes)

#             with tempfile.TemporaryDirectory() as temp_dir:
#                 output_video_path = os.path.join(temp_dir, "output_video.mp4")

#                 while True:
#                     ret, frame = cap.read()

#                     if not ret:
#                         break

#                     start_time = 3
#                     stop_time = 9
#                     current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

#                     if start_time <= current_time <= stop_time:
#                         user_text_combined = f"{user_name}"
#                         prize_text_combined = f"You've won a {random_prize}"

#                         max_width = 316
#                         max_height = 75

#                         frame = add_text_to_frame(frame, user_text_combined, (271, 864), max_width, max_height)
#                         frame = add_text_to_frame(frame, prize_text_combined, (271, 899), max_width, max_height)

#                     modified_frames.append(frame)

#                 cap.release()

#                 if modified_frames:
#                     out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (modified_frames[0].shape[1], modified_frames[0].shape[0]))

#                     for modified_frame in modified_frames:
#                         out.write(modified_frame)

#                     out.release()

#                     # Move the file to a non-temporary location before closing the temporary directory
#                     shutil.move(output_video_path, "static/output_video.mp4")

#                     socketio.emit('video_generated', {'video_path': "static/output_video.mp4", 'phone_number': sender_phone_number})

#                     return jsonify({"status": "success", "message": "Video generation completed", "video_path": "static/output_video.mp4"})
#                 else:
#                     return jsonify({"status": "error", "message": "No frames to process"})

#             return jsonify({"status": "error", "message": "Invalid file type. Please provide a valid video."})

#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)})

# @app.route('/result')
# def result():
#     # Assuming you have a variable 'video_path' containing the path to the personalized video
#     video_path = "static/output_video.mp4"
    
#     # Create a download link
#     download_link = {
#         'mp4': '/download_video?format=mp4',
#         'avi': '/download_video?format=avi',
#         'mov': '/download_video?format=mov',
#     }

#     return render_template('result.html', video_path=video_path, download_link=download_link)

# @app.route('/download_video')
# def download_video():
#     # Get the requested format from the query parameters
#     requested_format = request.args.get('format', 'mp4')

#     # Assuming you have a variable 'video_path' containing the path to the personalized video
#     video_path = "static/output_video.mp4"

#     # Define the content type based on the requested format
#     content_type = f'video/{requested_format}'

#     # Provide the video file for download
#     return send_file(video_path, as_attachment=True, mimetype=content_type)

# @app.route('/static/<filename>')
# def serve_video(filename):
#     return send_file(filename, as_attachment=True)

# if __name__ == '__main__':
#     socketio.run(app, debug=True)
