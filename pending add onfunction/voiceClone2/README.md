# Voice Cloning Web Application

A simple web application for voice cloning using Python Flask and the Coqui AI TTS library with XTTS-v2 model.

## Features

- Upload audio files (WAV, MP3, FLAC, OGG) as voice samples
- Enter Chinese text to be synthesized
- Generate cloned voice audio with Chinese pronunciation
- Simple web interface with audio playback
- GPU acceleration support (CUDA)

## Project Structure

```
voice_clone_project/
├── venv/                 # Virtual environment (create this)
├── output/               # Generated audio files
├── templates/            # HTML templates
│   └── index.html
├── uploads/              # Temporary upload storage (auto-created)
├── app.py               # Flask backend
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Prerequisites

1. **XTTS-v2 Model**: The model should be located at `C:\Users\SeanTeng\AppData\Local\tts\XTTS-v2\`
   - Ensure you have `config.json` and `model.pth` files in this directory

2. **Python 3.8+**: Make sure you have Python installed

3. **CUDA (Optional)**: For GPU acceleration, install CUDA-compatible PyTorch

## Setup Instructions

1. **Create and activate virtual environment:**
   ```powershell
   cd C:\Users\SeanTeng\Desktop\voiceClone2
   python -m venv venv
   venv\Scripts\Activate.ps1
   ```

2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Install PyTorch with CUDA support (optional, for GPU acceleration):**
   ```powershell
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

## Usage

1. **Start the Flask server:**
   ```powershell
   python app.py
   ```

2. **Open your web browser and navigate to:**
   ```
   http://localhost:5000
   ```

3. **Use the application:**
   - Upload a clear audio file of the voice you want to clone
   - Enter Chinese text in the text area
   - Click "Generate Voice" and wait for processing
   - Play the generated audio using the built-in player

## API Endpoint

**POST `/clone-voice`**
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `voice_sample`: Audio file (WAV, MP3, FLAC, OGG)
  - `text`: Text string to synthesize
- **Response:** `{"audio_url": "/output/generated_voice_xxxxx.wav"}`

## Troubleshooting

1. **Model Loading Issues:**
   - Ensure XTTS-v2 model files are in the correct location
   - Check that `config.json` and `model.pth` exist
   - The app will fallback to downloading the model if local files aren't found

2. **GPU Issues:**
   - If CUDA is not available, the app will automatically use CPU
   - For better performance, install CUDA-compatible PyTorch

3. **Audio Format Issues:**
   - Ensure uploaded audio files are in supported formats
   - For best results, use high-quality WAV files

4. **Memory Issues:**
   - The XTTS model requires significant RAM/VRAM
   - Close other applications if you encounter memory errors

## Notes

- Generated audio files are saved in the `output/` directory
- Each generation creates a unique filename to prevent overwriting
- The application targets Chinese (zh-cn) language output
- Processing time depends on text length and hardware capabilities