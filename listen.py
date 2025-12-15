import time
import json
import random
import requests
import sseclient

FIREBASE_BASE = "https://synaptix-e0fa0-default-rtdb.europe-west1.firebasedatabase.app"

def start_listener(path: str, on_change):
    url = f"{FIREBASE_BASE}/{path}.json"
    session = requests.Session()
    headers = {"Accept": "text/event-stream"}
    backoff = 1
    reconnect_attempts = 0
    while True:
        try:
            if reconnect_attempts == 0:
                print(f"Connecting to Firebase stream at /{path}...")
            else:
                print(f"Reconnecting (attempt {reconnect_attempts}) to /{path} after {backoff}s...")
            resp = session.get(url, stream=True, timeout=45, headers=headers)

            if resp.status_code != 200:
                print(f"Non-200 status {resp.status_code}. Body: {resp.text[:200]}")
                raise RuntimeError(f"Bad status {resp.status_code}")

            ct = resp.headers.get("Content-Type", "")
            if "event-stream" not in ct:
                print(f"Warning: Unexpected content-type '{ct}'. Firebase may have returned full JSON and closed connection.")

            client = sseclient.SSEClient(resp)
            backoff = 1  # reset after success
            reconnect_attempts = 0
            last_event_time = time.time()

            for event in client.events():
                # Heartbeats or empty frames
                if not event.data or event.data == "null":
                    # If idle for >120s, trigger a controlled reconnect
                    if time.time() - last_event_time > 120:
                        print("Idle >120s, refreshing stream...")
                        break
                    continue
                last_event_time = time.time()
                try:
                    data = json.loads(event.data)
                except json.JSONDecodeError:
                    continue
                on_change(data)

            # Loop ended naturally (break) -> reconnect
            reconnect_attempts += 1
            sleep_for = backoff + random.uniform(0, backoff / 2)
            print(f"Stream ended. Reconnecting in {sleep_for:.1f}s...")
            time.sleep(sleep_for)
            backoff = min(backoff * 2, 60)

        except KeyboardInterrupt:
            print("Stopped listener by user.")
            break
        except Exception as e:
            reconnect_attempts += 1
            sleep_for = backoff + random.uniform(0, backoff / 2)
            print(f"Stream error: {e}. Retry in {sleep_for:.1f}s (attempt {reconnect_attempts})")
            time.sleep(sleep_for)
            backoff = min(backoff * 2, 60)


def example_on_change(data: dict):
    """Example handler called whenever data at the path changes."""
    print("Change detected:")
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    # Listen to changes under /data
    start_listener("data", example_on_change)