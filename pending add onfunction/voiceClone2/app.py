import os
import uuid
import torch
from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
import tempfile
import torchaudio
import subprocess
import shutil

# Try to import pydub, but don't fail if it's not available
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    AudioSegment = None
    PYDUB_AVAILABLE = False
    print("Warning: pydub not available. M4A conversion will require ffmpeg.")

app = Flask(__name__)

# Configuration - Use absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'output')
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'flac', 'ogg', 'm4a'}

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Global variable to store the loaded model
model = None
device = None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_language(text):
    """Detect if text is primarily English or Chinese"""
    import re
    
    # Count Chinese characters (CJK ideographs)
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    
    # Count English letters
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    
    # Total meaningful characters
    total_chars = chinese_chars + english_chars
    
    if total_chars == 0:
        return "en"  # Default to English if no recognizable characters
    
    # If more than 30% Chinese characters, use Chinese
    if chinese_chars / total_chars > 0.3:
        return "zh-cn"
    else:
        return "en"

def convert_audio_to_wav(input_path, output_path):
    """Convert audio file to WAV format using ffmpeg or pydub fallback"""
    try:
        # Try using ffmpeg first (more reliable)
        if shutil.which('ffmpeg'):
            print(f"Converting {input_path} to WAV using ffmpeg...")
            result = subprocess.run([
                'ffmpeg', '-i', input_path, '-acodec', 'pcm_s16le', 
                '-ar', '22050', '-ac', '1', output_path, '-y'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("Conversion successful with ffmpeg")
                return True
            else:
                print(f"ffmpeg failed: {result.stderr}")
        
        # Fallback to pydub
        if PYDUB_AVAILABLE and AudioSegment is not None:
            try:
                print(f"Converting {input_path} to WAV using pydub...")
                
                # Load audio file
                audio = AudioSegment.from_file(input_path)
                
                # Convert to mono and set sample rate to 22050 Hz
                audio = audio.set_channels(1).set_frame_rate(22050)
                
                # Export as WAV
                audio.export(output_path, format="wav")
                print("Conversion successful with pydub")
                return True
                
            except Exception as e:
                print(f"pydub conversion failed: {e}")
                return False
        else:
            print("pydub not available. Please install: pip install pydub")
            return False
            
    except Exception as e:
        print(f"Audio conversion failed: {e}")
        return False

def load_xtts_model():
    """Load the XTTS model using automatic download"""
    global model, device
    
    print("Loading XTTS model...")
    
    # Check if CUDA is available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    gpu_enabled = device == "cuda"
    print(f"Using device: {device}")
    
    try:
        # Use TTS API to download and load the model automatically
        from TTS.api import TTS
        print("Downloading and loading XTTS model (this may take a few minutes)...")
        
        # Set environment variable to bypass license prompt automatically
        os.environ['COQUI_TOS_AGREED'] = "1"
        
        # Let TTS handle the download automatically
        model = TTS(
            model_name="tts_models/multilingual/multi-dataset/xtts_v2",
            progress_bar=True
        )
        model.to(device)
        
        print("XTTS model loaded successfully!")
        
    except Exception as e:
        # Enhanced error reporting
        import traceback
        print("===================================")
        print("AN ERROR OCCURRED DURING MODEL LOADING:")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        print("--- Full Traceback ---")
        traceback.print_exc()  # This will print the complete error stack
        print("===================================")
        print("Model loading failed. Voice cloning will not work.")
        model = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/clone-voice', methods=['POST'])
def clone_voice():
    global model
    
    if model is None:
        return jsonify({'error': 'Model not loaded. Please restart the server.'}), 500
    
    # Check if the request has the required parts
    if 'voice_sample' not in request.files or 'text' not in request.form:
        return jsonify({'error': 'Missing voice_sample file or text'}), 400
    
    voice_file = request.files['voice_sample']
    text = request.form['text']
    user_language = request.form.get('language', None)  # Optional language override
    
    if voice_file.filename == '':
        return jsonify({'error': 'No voice sample file selected'}), 400
    
    if not text.strip():
        return jsonify({'error': 'No text provided'}), 400
    
    if voice_file and allowed_file(voice_file.filename):
        try:
            # Save the uploaded voice sample temporarily
            filename = secure_filename(voice_file.filename or "audio_file")
            temp_voice_path = os.path.join(UPLOAD_FOLDER, f"temp_{uuid.uuid4()}_{filename}")
            voice_file.save(temp_voice_path)
            
            # Check if we need to convert the audio format
            file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            processed_voice_path = temp_voice_path
            converted_path = None
            
            if file_extension == 'm4a':
                # Convert M4A to WAV
                converted_path = os.path.join(UPLOAD_FOLDER, f"converted_{uuid.uuid4()}.wav")
                print(f"Converting M4A file to WAV format...")
                
                if convert_audio_to_wav(temp_voice_path, converted_path):
                    processed_voice_path = converted_path
                    print("Audio conversion completed successfully")
                else:
                    raise Exception("Failed to convert M4A file. Please use WAV, MP3, FLAC, or OGG format instead.")
            
            # Generate unique output filename
            output_filename = f"generated_voice_{uuid.uuid4().hex}.wav"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            
            print(f"Processing voice cloning for text: {text[:50]}...")
            
            # Verify the voice sample file exists and get info
            if os.path.exists(processed_voice_path):
                file_size = os.path.getsize(processed_voice_path)
                print(f"✅ Voice sample ready: {processed_voice_path}")
                print(f"   File size: {file_size} bytes")
                print(f"   Using {'converted' if converted_path else 'original'} audio file")
            else:
                raise Exception(f"Voice sample file not found: {processed_voice_path}")
            
            # Detect language or use user selection
            if user_language and user_language in ['en', 'zh-cn']:
                language = user_language
                print(f"Using user-selected language: {language}")
            else:
                language = detect_language(text)
                print(f"Auto-detected language: {language}")
            
            print(f"🎤 Starting voice cloning with speaker sample: {os.path.basename(processed_voice_path)}")
            
            # Use TTS API method (compatible with TTS() object)
            model.tts_to_file(
                text=text,
                speaker_wav=processed_voice_path,
                language=language,
                file_path=output_path
            )
            
            print(f"✅ Voice cloning completed successfully!")
            
            # Clean up temporary files
            if os.path.exists(temp_voice_path):
                os.remove(temp_voice_path)
            if converted_path is not None and os.path.exists(converted_path):
                os.remove(converted_path)
            
            # Return the URL to the generated audio
            audio_url = f"/output/{output_filename}"
            print(f"Voice cloning completed. Audio saved to: {output_path}")
            
            return jsonify({'audio_url': audio_url})
            
        except Exception as e:
            # Clean up temporary files in case of error
            if 'temp_voice_path' in locals() and os.path.exists(temp_voice_path):
                os.remove(temp_voice_path)
            if 'converted_path' in locals() and converted_path is not None and os.path.exists(converted_path):
                os.remove(converted_path)
            
            print(f"Error during voice cloning: {e}")
            return jsonify({'error': f'Voice cloning failed: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type. Please upload a WAV, MP3, FLAC, OGG, or M4A file.'}), 400

@app.route('/output/<filename>')
def output_file(filename):
    try:
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        print(f"Attempting to serve file: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")
        
        if not os.path.exists(file_path):
            print(f"ERROR: File not found at {file_path}")
            print(f"OUTPUT_FOLDER contents: {os.listdir(OUTPUT_FOLDER)}")
            return jsonify({'error': 'File not found'}), 404
            
        return send_from_directory(OUTPUT_FOLDER, filename)
    except Exception as e:
        print(f"Error serving file: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Load the model when the server starts
    load_xtts_model()
    
    if model is None:
        print("WARNING: Model failed to load. The server will start but voice cloning will not work.")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)