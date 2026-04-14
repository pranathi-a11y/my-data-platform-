import os
from supabase import create_client

# Supabase configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://gwctkzynfvgqoznrejruz.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

def clean_batch():
    print("🧹 Starting batch cleaning from Supabase...")
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # 1. Fetch raw events
        res = supabase.table("events").select("*").eq("status", "raw").execute()
        events = res.data
        
        if not events:
            print("ℹ️ No new raw events to process.")
            return

        print(f"🔄 Processing {len(events)} events...")
        
        # 2. Update status to 'clean' for each event
        for event in events:
            supabase.table("events").update({"status": "clean"}).eq("event_id", event["event_id"]).execute()
            
        print(f"✅ Successfully cleaned {len(events)} events in Supabase!")
        
    except Exception as e:
        print(f"❌ Error during cleaning: {e}")

if __name__ == "__main__":
    clean_batch()
