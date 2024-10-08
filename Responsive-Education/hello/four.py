from flask import Flask, Response, render_template, jsonify, Blueprint
import cv2
from keras.models import load_model
import numpy as np

app = Flask(__name__)
four_bp = Blueprint('four', __name__, template_folder='templates')

# Load the trained model and face detector
face_classifier = cv2.CascadeClassifier(r"/main/Responsive-Education/haarcascade_frontalface_default.xml")
classifier = load_model(r"/main/Responsive-Education/model.h5")
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']

emotion_tip = ""  # Global variable to store the current emotion tip

def get_tip(emotion):
    tips = {
        "Angry": "Practice mindfulness or meditation exercises to help manage your anger. Consider listening to calming music or going for a short walk.",
        "Disgust": "Remind yourself that not everything is perfect, and it's okay to feel disgusted. Try to identify the source and understand your reaction, then move on to something more pleasant.",
        "Fear": "Address your fear by talking to someone you trust or writing down your thoughts. Practice deep breathing and remind yourself that the feeling will pass.",
        "Happy": "Embrace the moment! Keep a gratitude journal or engage in activities that amplify your happiness, such as spending time with loved ones or pursuing a hobby.",
        "Neutral": "Consider setting goals or planning your day. Engage in light activities like reading or listening to soft music to maintain your neutral state.",
        "Sad": "Try engaging in creative activities like drawing, writing, or playing music. Exercise can also help release endorphins and improve your mood.",
        "Surprise": "Reflect on the surprise and consider how it might bring positive changes. Keep an optimistic outlook and explore new possibilities."
    }
    return tips.get(emotion, "No suggestion available.")

def generate_frames():
    global emotion_tip
    cap = cv2.VideoCapture(0)  # Open the webcam
    
    # Set webcam resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    
    while True:
        success, frame = cap.read()  # Read a frame from the webcam
        if not success:
            break

        # Resize the frame for quicker loading
        frame = cv2.resize(frame, (320, 240))  # Resize frame to smaller size

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)

            if np.sum([roi_gray]) != 0:
                roi = roi_gray.astype('float') / 255.0
                roi = np.expand_dims(roi, axis=0)
                prediction = classifier.predict(roi)[0]
                label = emotion_labels[prediction.argmax()]
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Update the emotion tip
                emotion_tip = get_tip(label)
            else:
                cv2.putText(frame, 'No Faces', (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Encode the frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@four_bp.route('/four1')
def four():
    return render_template('index2.html')

@four_bp.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@four_bp.route('/get_tip')
def get_tip_route():
    global emotion_tip
    return jsonify(emotion_tip)  # Return the emotion tip as JSON

@four_bp.route('/start_video', methods=['POST'])
def start_video():
    # This is where you could add additional logic if needed for starting the video
    return '', 204

@four_bp.route('/stop_video', methods=['POST'])
def stop_video():
    # This is where you could add additional logic if needed for stopping the video
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
