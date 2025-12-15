import requests
from datetime import datetime

url = "https://synaptix-e0fa0-default-rtdb.europe-west1.firebasedatabase.app/data.json"

# Send data
data = {
    "message": "ciao fefeFirebase",
    "value": 123565,
    "timestamp": datetime.now().isoformat()
}

try:
    print("Sending data to Firebase...")
    response = requests.put(url, json=data, timeout=10)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success! Data saved directly to /data")
        print(f"Response: {result}")
    else:
        print(f"❌ Error: Status code {response.status_code}")
        print(response.text)
        
except requests.exceptions.Timeout:
    print("❌ Connection timeout - Check your internet connection")
except requests.exceptions.ConnectionError:
    print("❌ Connection error - Check your internet or firewall")
except Exception as e:
    print(f"❌ Error: {e}")

