import json
import time
import uuid
import os
from datetime import datetime
from supabase import create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://gwctkzynfvgqoznrejruz.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

def generate_event():
    return {
        "event_id": str(uuid.uuid4()),
        "user_id": f"user_{uuid.uuid4().hex[:4]}",
        "event_type": "click",
        "timestamp": datetime.now().isoformat(),
        "url": "/products/electronics",
        "status": "raw"
    }

def start_ingestion():
    db = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("📡 Simulating ingestion to Supabase...")

    try:
        while True:
            event = generate_event()
            db.table("events").insert(event).execute()
            print(f"✅ Ingested event: {event['event_id']}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n🛑 Ingestion stopped.")

if __name__ == "__main__":
    start_ingestion()
