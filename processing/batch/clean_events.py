import pandas as pd
import glob
import json
import os
from datetime import datetime

RAW_PATH = "data_lake/raw/user_clicks/*.json"
CLEAN_PATH = "data_lake/clean/user_clicks"

def clean_batch():
    print("🧹 Starting batch cleaning...")
    
    # 1. Read all JSON files from raw path
    files = glob.glob(RAW_PATH)
    if not files:
        print("ℹ️ No new files to process.")
        return

    data = []
    for f in files:
        with open(f, 'r') as file:
            data.append(json.load(file))
    
    df = pd.DataFrame(data)
    
    # 2. Basic Cleaning
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.drop_duplicates(subset=['event_id'])
    
    # 3. Write to Clean Layer
    os.makedirs(CLEAN_PATH, exist_ok=True)
    output_file = f"{CLEAN_PATH}/cleaned_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
    
    # Using CSV if parquet engine is missing, but pandas 1.5+ usually has it
    try:
        df.to_parquet(output_file, index=False)
        print(f"✅ Saved cleaned data to: {output_file}")
    except ImportError:
        output_file = output_file.replace(".parquet", ".csv")
        df.to_csv(output_file, index=False)
        print(f"✅ Saved cleaned data to: {output_file} (CSV fallback)")

    # 4. Optional: Archive or delete processed raw files
    # for f in files:
    #     os.remove(f)

if __name__ == "__main__":
    clean_batch()
