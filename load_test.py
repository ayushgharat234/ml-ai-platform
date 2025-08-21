import asyncio
import httpx
import time
import random

# --- Configuration ---
# The base URL of your API, running behind the Nginx proxy
API_BASE_URL = "http://localhost"

# IMPORTANT: The endpoint for making predictions.
# Your Nginx proxies `location /` to the API. You need to replace `/predict`
# with the actual endpoint in your API code (e.g., FastAPI/Flask) that
# triggers the Celery task.
PREDICT_ENDPOINT = "/predict/"

# Number of concurrent requests to send
NUM_REQUESTS = 2000

# Number of features your model expects.
# This should match the model used in `worker/tasks.py`.
NUM_FEATURES = 4


async def make_prediction_request(client: httpx.AsyncClient, request_num: int):
    """Sends a single prediction request to the API."""
    # Generate some random feature data for the request
    features = [random.uniform(0.0, 10.0) for _ in range(NUM_FEATURES)]
    payload = {"features": features}

    print(f"[Request {request_num:02d}] Sending request...")

    try:
        start_time = time.time()
        # The request is sent to Nginx, which forwards it to your API
        response = await client.post(f"{API_BASE_URL}{PREDICT_ENDPOINT}", json=payload, timeout=15.0)
        duration = time.time() - start_time

        # --- Interpreting the Response ---
        if response.status_code == 202:  # Accepted: The task was successfully created
            task_id = response.json().get("task_id")
            print(f"[Request {request_num:02d}] SUCCESS ({response.status_code}) -> Task ID: {task_id} (took {duration:.2f}s)")
            return task_id
        elif response.status_code == 503:  # Service Unavailable: Rate limited by Nginx
            print(f"[Request {request_num:02d}] FAILED  ({response.status_code}) -> Rate limited by Nginx. (took {duration:.2f}s)")
        else:
            print(f"[Request {request_num:02d}] FAILED  ({response.status_code}) -> Response: {response.text} (took {duration:.2f}s)")

    except httpx.ReadTimeout:
        print(f"[Request {request_num:02d}] FAILED  -> Request timed out.")
    except httpx.ConnectError:
        print(f"[Request {request_num:02d}] FAILED  -> Connection error. Is the service running?")
    except Exception as e:
        print(f"[Request {request_num:02d}] FAILED  -> An unexpected error occurred: {e}")

    return None


async def main():
    """Main function to run the load test."""
    print("--- Starting API Load Test ---")
    print(f"Target: {API_BASE_URL}{PREDICT_ENDPOINT}")
    print(f"Sending {NUM_REQUESTS} concurrent requests to test rate limiting (5r/s, burst=10)...")
    print("-" * 30)

    # Use httpx.AsyncClient for connection pooling and performance
    async with httpx.AsyncClient() as client:
        tasks = [make_prediction_request(client, i + 1) for i in range(NUM_REQUESTS)]
        results = await asyncio.gather(*tasks)

    print("-" * 30)
    print("--- Load Test Finished ---")

    task_ids = [res for res in results if res is not None]
    print(f"\nSuccessfully created {len(task_ids)} Celery tasks.")

if __name__ == "__main__":
    asyncio.run(main())