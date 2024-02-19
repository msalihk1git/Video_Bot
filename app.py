from flask import Flask, request, jsonify
import cv2
import os
import random
import requests

app = Flask(__name__)

token = os.environ.get("WHATSAPP_TOKEN")
verify_token = os.environ.get("VERIFY_TOKEN")
phone_number_id = None  # Define phone_number_id globally

chat_sessions = {}  # Store user chat sessions

video_path = r"sample_video2.mp4"


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


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(json.dumps(data, indent=2))

    if "object" in data:
        if (
            "entry" in data
            and data["entry"]
            and "changes" in data["entry"][0]
            and data["entry"][0]["changes"]
            and "value" in data["entry"][0]["changes"][0]
            and "messages" in data["entry"][0]["changes"][0]["value"]
            and data["entry"][0]["changes"][0]["value"]["messages"][0]
        ):
            global phone_number_id
            phone_number_id = data["entry"][0]["changes"][0]["value"]["metadata"]["phone_number_id"]
            sender = data["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
            msg_body = data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]

            # Check if there is an existing session for the user
            if sender not in chat_sessions:
                # If no session, initiate chat by asking for the user's name
                initiate_chat(sender)
            elif chat_sessions[sender]["waitingForName"]:
                # If waiting for the user's name, process the name and send personalized video
                process_and_send_personalized_video(sender, msg_body)
                # Mark the user as having completed the interaction to prevent further responses
                chat_sessions[sender]["interactionCompleted"] = True
            elif chat_sessions[sender]["interactionCompleted"]:
                # If the interaction is completed, do not initiate a new chat session
                pass
            else:
                # If there is an existing session, handle the message accordingly
                handle_user_message(sender, msg_body)

            return jsonify({"status": "success"}), 200

    return jsonify({"status": "not found"}), 404


@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == verify_token:
            print("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            return "Forbidden", 403

    return "Not Found", 404


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

            possible_prizes = ["10% OFF ON FOOTWEAR", "20% OFFER ON JEANS", "50% OFFER ON INNERWEAR",
                               "75% OFFER ON TOPWEAR", "25% OFF ON TELEVISION", "GIFT CARD",
                               "45% OFFER ON TV"]
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
                    frame = add_text_to_frame(frame, prize_text_combined, (271, 899), max_width, max_height)

                modified_frames.append(frame)

            cap.release()

            if modified_frames:
                output_video_path = "static/output_video.mp4"
                out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'),
                                      fps, (modified_frames[0].shape[1], modified_frames[0].shape[0]))

                for modified_frame in modified_frames:
                    out.write(modified_frame)

                out.release()

                # Send the personalized video URL as a reply
                send_message(sender_phone_number, f"Here's your personalized video: {output_video_path}")

                return jsonify({"status": "success", "message": "Video generation completed",
                                "video_path": output_video_path})
            else:
                return jsonify({"status": "error", "message": "No frames to process"})

        return jsonify({"status": "error", "message": "Invalid file type. Please provide a valid video."})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


def initiate_chat(user):
    # Send initial message asking for the user's name
    send_message(user, "Enter your name?")
    # Update chat session to track that we are waiting for the user's name
    chat_sessions[user] = {"waitingForName": True}


def send_video_message(user):
    # Check if the video has already been sent to avoid sending it again
    if "videoSent" not in chat_sessions[user]:
        # Construct the video URL correctly
        video_url = "https://yourdomain.com/static/output_video.mp4"  # Update with your domain and path

        requests.post(
            f"https://graph.facebook.com/v12.0/{phone_number_id}/messages?access_token={token}",
            json={
                "messaging_product": "whatsapp",
                "to": user,
                "type": "video",
                "video": {
                    "link": video_url,
                },
            },
            headers={"Content-Type": "application/json"},
        )

        # Mark the video as sent to prevent sending it again
        chat_sessions[user]["videoSent"] = True

def send_message(user, message):
    requests.post(
        f"https://graph.facebook.com/v12.0/{phone_number_id}/messages?access_token={token}",
        json={
            "messaging_product": "whatsapp",
            "to": user,
            "text": {"body": message},
        },
        headers={"Content-Type": "application/json"},
    )


def handle_user_message(user, message):
    # The chatbot does not respond further after sending the video,
    # so you can leave this function empty or handle it as needed.
    pass


if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 1337)))
