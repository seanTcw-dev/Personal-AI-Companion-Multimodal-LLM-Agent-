
import dateparser
from datetime import datetime

text = "i have a meeting at tomorrow 8am"
print(f"Testing text: '{text}'")

# Current settings
settings = {
    'PREFER_DATES_FROM': 'future',
    'RELATIVE_BASE': datetime.now(),
    'TIMEZONE': 'UTC',
    'PREFER_DAY_OF_MONTH': 'first'
}

print("\n--- Test 1: dateparser.parse (current method) ---")
result = dateparser.parse(text, settings=settings)
print(f"Result: {result}")

print("\n--- Test 2: dateparser.search.search_dates ---")
try:
    from dateparser.search import search_dates
    results = search_dates(text, settings=settings)
    print(f"Results: {results}")
except ImportError:
    print("search_dates not available")

print("\n--- Test 3: Simplified text 'tomorrow 8am' ---")
result_simple = dateparser.parse("tomorrow 8am", settings=settings)
print(f"Result: {result_simple}")
