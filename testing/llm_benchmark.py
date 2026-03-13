import time
import json
import os
import statistics
from pathlib import Path
import ollama

# ==========================================
# CONSTANTS & CONFIGURATION
# ==========================================
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Target A: Larger, more capable local model
TARGET_A_MODEL = "gemma3:4b"

# Target B: The system's actual model (our proposed method)
TARGET_B_MODEL = "llama3.2:3b"

# Create a single persistent client (exactly like ollama_service.py does)
client = ollama.Client(host=OLLAMA_BASE_URL)

# Manually crafted tool descriptions (clearer than raw JSON definitions)
TOOLS_SUMMARY = """- Name: calendar
  Description: Schedule meetings, check weekly plans, or set reminders on Google Calendar.
- Name: pdf_analysis
  Description: Read, summarize, explain, or extract main points from ANY uploaded documents, PDFs, pages, or reports.
- Name: url_opener
  Description: Open specific URLs, launch websites, or search on the browser.
- Name: briefing
  Description: Get a daily briefing with news, emails, and schedule summary.
- Name: file_management
  Description: Create or modify local text files. (Do NOT use this for reading PDFs or reports)
"""

# The exact prompt structure from ai_service.py
def build_router_prompt(message):
    return (
        f"You are a strict Intent Classification Agent. You do NOT speak. You ONLY output JSON.\n\n"
        f"AVAILABLE TOOLS:\n{TOOLS_SUMMARY}\n\n"
        f"EXAMPLES:\n"
        f"User: \"explain this PDF file to me\"\nOutput: {{\"intent\": \"pdf_analysis\"}}\n"
        f"User: \"what's the news for today?\"\nOutput: {{\"intent\": \"briefing\"}}\n"
        f"User: \"can you set a reminder for my doctor appointment?\"\nOutput: {{\"intent\": \"calendar\"}}\n"
        f"User: \"tell me a joke\"\nOutput: {{\"intent\": \"CHAT\"}}\n\n"
        f"USER REQUEST: \"{message}\"\n\n"
        f"INSTRUCTIONS:\n"
        f"Classify the USER REQUEST into one of the tool names. Output ONLY a valid JSON object. Do not add explanations."
    )

# ==========================================
# DATASET
# ==========================================
TEST_DATA = [
    # --- CHAT (5) ---
    {"prompt": "hello anyone there", "expected": "CHAT"},
    {"prompt": "how are you doing today?", "expected": "CHAT"},
    {"prompt": "you are acting a bit weird", "expected": "CHAT"},
    {"prompt": "tell me a joke", "expected": "CHAT"},
    {"prompt": "what is the meaning of life?", "expected": "CHAT"},

    # --- CALENDAR (5) ---
    {"prompt": "schedule a meeting with John tomorrow at 5pm", "expected": "calendar"},
    {"prompt": "what do I have planned for this week?", "expected": "calendar"},
    {"prompt": "can you set a reminder for my doctor appointment?", "expected": "calendar"},
    {"prompt": "add lunch with Sarah to my calendar on Friday", "expected": "calendar"},
    {"prompt": "remind me about the team standup every Monday", "expected": "calendar"},

    # --- PDF ANALYSIS (4) ---
    {"prompt": "summarize the uploaded document", "expected": "pdf_analysis"},
    {"prompt": "what are the key takeaways from page 4?", "expected": "pdf_analysis"},
    {"prompt": "explain this PDF file to me", "expected": "pdf_analysis"},
    {"prompt": "extract the main points from the report", "expected": "pdf_analysis"},

    # --- URL OPENER (4) ---
    {"prompt": "open google.com", "expected": "url_opener"},
    {"prompt": "launch youtube", "expected": "url_opener"},
    {"prompt": "go to reddit.com", "expected": "url_opener"},
    {"prompt": "open twitter for me", "expected": "url_opener"},

    # --- BRIEFING (2) ---
    {"prompt": "give me a daily briefing", "expected": "briefing"},
    {"prompt": "what's the news for today?", "expected": "briefing"},
]

# ==========================================
# CORE FUNCTION — Uses ollama library (same as ollama_service.py)
# ==========================================
def call_ollama(prompt_text, model):
    """
    Call a local Ollama model using the ollama Python library.
    This mirrors the exact approach used in ollama_service.py:
        self.client.generate(model=..., prompt=..., format='json', stream=False, options={})
    """
    start_time = time.time()
    try:
        response = client.generate(
            model=model,
            prompt=prompt_text,
            format="json",
            stream=False,
            options={
                "temperature": 0.0,
                "num_predict": 50  # We only need {"intent":"X"}, cap output tokens
            }
        )
        latency = time.time() - start_time

        raw_text = response['response'].strip()
        try:
            parsed = json.loads(raw_text)
            return parsed.get("intent", "ERROR"), latency
        except json.JSONDecodeError:
            return f"PARSE_ERROR: {raw_text[:60]}", latency

    except Exception as e:
        latency = time.time() - start_time
        return f"API_ERROR: {str(e)}", latency

# ==========================================
# MAIN TEST LOOP
# ==========================================
def run_benchmark():
    label_a = "Gemma3 4B (gemma3:4b)"
    label_b = "LLaMA 3.2 3B (llama3.2:3b)"

    models = [
        (label_a, TARGET_A_MODEL),
        (label_b, TARGET_B_MODEL),
    ]

    print(f"Starting Benchmark on {len(TEST_DATA)} User Prompts...")
    print(f"Target A: {label_a}")
    print(f"Target B: {label_b} — System Proposed Method")
    print(f"Using: ollama.Client (same as production system)")
    print(f"NOTE: Models are tested sequentially to avoid GPU model-swap overhead.\n")

    results = {
        label_a: {"correct": 0, "latencies": [], "errors": []},
        label_b: {"correct": 0, "latencies": [], "errors": []}
    }

    for label, model_name in models:
        print(f"\n{'='*55}")
        print(f"  Testing: {label}")
        print(f"{'='*55}")

        # Warmup: load the model into GPU before timing
        print(f"  ⏳ Warming up {model_name} (loading into GPU)...")
        call_ollama("Say hi", model_name)
        print(f"  ✅ Model loaded. Starting timed tests...\n")

        for i, item in enumerate(TEST_DATA):
            router_prompt = build_router_prompt(item["prompt"])
            intent, lat = call_ollama(router_prompt, model_name)

            results[label]["latencies"].append(lat)
            if intent == item["expected"]:
                results[label]["correct"] += 1
                print(f"  [{i+1}/{len(TEST_DATA)}] ✅ '{item['prompt']}' → {intent} ({lat*1000:.0f}ms)")
            else:
                results[label]["errors"].append({"prompt": item["prompt"], "expected": item["expected"], "got": intent})
                print(f"  [{i+1}/{len(TEST_DATA)}] ❌ '{item['prompt']}' → Got '{intent}', expected '{item['expected']}' ({lat*1000:.0f}ms)")

    # ==========================================
    # PRINT REPORT
    # ==========================================
    print("\n" + "="*55)
    print("  BENCHMARK REPORT (For Chapter 6 Tables)")
    print("="*55)

    for label in [label_a, label_b]:
        correct = results[label]["correct"]
        total = len(TEST_DATA)
        acc = (correct / total) * 100
        avg_lat = statistics.mean(results[label]["latencies"]) * 1000

        print(f"\n📊 {label}")
        print(f"   Accuracy      : {acc:.2f}% ({correct}/{total})")
        print(f"   Avg Latency   : {avg_lat:.2f} ms")

        if results[label]["errors"]:
            print(f"   Failed Cases  : {len(results[label]['errors'])}")
            for e in results[label]["errors"][:5]:
                print(f"     - '{e['prompt']}' → expected '{e['expected']}', got '{e['got']}'")

    # Save to file
    output_path = Path(__file__).parent / "llm_benchmark_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)
    print(f"\n💾 Full results saved to {output_path}")

if __name__ == "__main__":
    run_benchmark()
