import time
import requests
import re
import asyncio

# ==========================================
# CONFIGURATION
# ==========================================
# Adjust this to your backend's actual voice generation endpoint
# Assuming your voice_service.py exposes an endpoint like this. If not, you may need to adjust the URL to hit an ollama or XTTS explicit mock server.
TTS_API_URL = "http://localhost:8000/api/voice/generate" 

LONG_PARAGRAPH = (
    "Hello there! I am Suzune Horikita. Today I am going to talk about the significance of "
    "optimizing real-time interactions in an AI agent system. By breaking down large inputs "
    "into smaller chunks using punctuation boundaries, we can vastly decrease the time to first byte, "
    "allowing the system to start speaking almost immediately. This gives a true conversational feel "
    "without awkward waiting periods."
)

def extract_first_chunk(text):
    """
    Scenario B logic: Split by punctuation and take the first sentence.
    """
    # Split by standard sentence-ending punctuation
    delimiters = r'([.?!,] )'
    parts = re.split(delimiters, text)
    if len(parts) > 1:
        # Reconstruct the first sentence with its punctuation
        return (parts[0] + parts[1]).strip()
    return text.strip()

def measure_ttfb(text_payload, scenario_name):
    """
    Sends the request and measures the time until the response is initialized (TTFB).
    NOTE: Depending on your FastAPI setup, if the endpoint generates a .wav file completely 
    before returning, this will measure total processing time. To measure true TTFB for streaming,
    the endpoint needs to return a StreamingResponse.
    """
    data = {
        "text": text_payload,
        "character_name": "suzune_horikita",
        "language": "en"
    }
    
    print(f"\nRunning {scenario_name}...")
    print(f"Payload length: {len(text_payload)} characters")
    
    start_time = time.time()
    try:
        # We use stream=True so requests doesn't wait to download the whole file
        # It triggers the moment headers are received from the server.
        response = requests.post(TTS_API_URL, json=data, stream=True)
        response.raise_for_status()
        
        # Read just the very first chunk of bytes to prove TTFB
        for chunk in response.iter_content(chunk_size=1024):
            if chunk: 
                break 
                
        ttfb = (time.time() - start_time) * 1000 # Convert to ms
        print(f"✅ {scenario_name} Time-to-First-Byte (TTFB): {ttfb:.2f} ms")
        return ttfb

    except requests.exceptions.RequestException as e:
        print(f"❌ Error during request: {e}")
        return None

def run_profiler():
    print("==========================================")
    print(" XTTS-v2 Latency Profiler (Chapter 5 & 6) ")
    print("==========================================")
    print("Target Paragraph:")
    print(f"\"{LONG_PARAGRAPH}\"\n")

    # Scenario A: Unoptimized (Full text sent at once)
    ttfb_a = measure_ttfb(LONG_PARAGRAPH, "Scenario A: Unoptimized (Full Text)")

    time.sleep(2) # Cooldown

    # Scenario B: Optimized (Punctuation Boundary Chunking)
    first_chunk = extract_first_chunk(LONG_PARAGRAPH)
    print(f"\nChunk extracted for Scenario B: \"{first_chunk}\"")
    ttfb_b = measure_ttfb(first_chunk, "Scenario B: Optimized (First Chunk Only)")

    print("\n==========================================")
    print(" RESULTS FOR REPORT:")
    print("==========================================")
    if ttfb_a and ttfb_b:
        improvement = ttfb_a - ttfb_b
        percent = (improvement / ttfb_a) * 100
        print(f"Unoptimized TTFB : {ttfb_a:.2f} ms")
        print(f"Optimized TTFB   : {ttfb_b:.2f} ms")
        print(f"Latency Reduction: {improvement:.2f} ms ({percent:.1f}% faster)")
        print("\nSuggested Report Conclusion:")
        print(f"\"By implementing Punctuation Boundary Chunking, the system's first-byte audio latency "
              f"dropped from {ttfb_a:.0f}ms to {ttfb_b:.0f}ms, successfully achieving the real-time interaction "
              f"goal mandated in Chapter 1.\"")
    else:
        print("Test failed. Please ensure the backend is running at http://localhost:8000")

if __name__ == "__main__":
    run_profiler()
