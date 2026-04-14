import json
import time
import uuid
import os
from datetime import datetime

RAW_PATH = "data_lake/raw/user_clicks"

def generate_event():
    return {
        "event_id": str(uuid.uuid4()),
        "user_id": f"user_{uuid.uuid4().hex[:4]}",
        "event_type": "click",
        "timestamp": datetime.now().isoformat(),
        "url": "/products/electronics"
    }

def start_ingestion():
    print(f"📡 Simulating ingestion to {RAW_PATH}...")
    # Ensure directory exists
    os.makedirs(RAW_PATH, exist_ok=True)
    
    try:
        while True:
            event = generate_event()
            # Create a unique filename for each event
            filename = f"{RAW_PATH}/event_{int(time.time()*1000)}.json"
            with open(filename, 'w') as f:
                json.dump(event, f)
            print(f"✅ Ingested event: {event['event_id']}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n🛑 Ingestion stopped.")

if __name__ == "__main__":
    start_ingestion()
