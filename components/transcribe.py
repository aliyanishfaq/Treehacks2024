from flask import Flask, request, jsonify
import whisper
import os
import tempfile

app = Flask(__name__)

# Load the Whisper model (consider doing this outside of your request handling for efficiency)
model = whisper.load_model("base")

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the file to a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    file.save(temp_file.name)

    try:
        # Transcribe the audio file
        result = model.transcribe(temp_file.name)
        transcription = result["text"]
    finally:
        # Make sure to clean up the temporary file
        os.unlink(temp_file.name)

    return jsonify({"transcription": transcription})

if __name__ == '__main__':
    app.run(debug=True)
