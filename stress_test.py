import requests
import time
import concurrent.futures

API_URL = "http://localhost:8000"

def send_request(i):
    text = f"This is request number {i}. I hope the server can handle it!"
    response = requests.post(f"{API_URL}/analyze", json={"texts": [text]})
    return i, response.json()

print(f"🚀 Launching Stress Test against {API_URL}...")
start_time = time.time()

# Send 50 requests in parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(send_request, i) for i in range(50)]
    
    for future in concurrent.futures.as_completed(futures):
        i, res = future.result()
        print(f"✅ Request {i} Queued: {res['task_id']}")

print(f"\n⚡ All 50 requests sent in {time.time() - start_time:.2f} seconds!")
print("The API is still responsive. Check the worker logs to see them processing!")