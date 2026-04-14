from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import glob

app = FastAPI(title="Data Platform Serving API")

# Mock data (in a real scenario, this would come from the data warehouse or NoSQL store)
mock_user_profiles = [
    {"user_id": "user_1", "name": "Alice Smith", "plan": "premium", "last_active": datetime.now().isoformat()},
    {"user_id": "user_2", "name": "Bob Johnson", "plan": "free", "last_active": datetime.now().isoformat()},
]

class UserProfile(BaseModel):
    user_id: str
    name: str
    plan: str
    last_active: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the Data Platform Serving API"}

@app.get("/users/{user_id}", response_model=UserProfile)
def get_user_profile(user_id: str):
    user = next((u for u in mock_user_profiles if u["user_id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")
    return user

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/metrics")
def get_metrics():
    # Real-time metrics from our local data lake
    raw_files = glob.glob("data_lake/raw/user_clicks/*.json")
    clean_files = glob.glob("data_lake/clean/user_clicks/*.parquet") + glob.glob("data_lake/clean/user_clicks/*.csv")
    
    return {
        "ingested_events_count": len(raw_files),
        "processed_batches_count": len(clean_files),
        "last_updated": datetime.now().isoformat()
    }

@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Data Platform Dashboard</title>
            <meta http-equiv="refresh" content="5">
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; display: flex; flex-direction: column; align-items: center; padding: 50px; }
                .card-container { display: flex; gap: 20px; }
                .card { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; width: 250px; }
                .card h2 { color: #555; font-size: 1.2rem; margin-bottom: 10px; }
                .card .number { font-size: 3rem; font-weight: bold; color: #007bff; }
                .status { margin-top: 20px; color: #888; font-size: 0.9rem; }
                h1 { color: #333; margin-bottom: 40px; }
            </style>
        </head>
        <body>
            <h1>🚀 Real-Time Data Platform Dashboard</h1>
            <div class="card-container">
                <div class="card">
                    <h2>Ingested Events</h2>
                    <div id="ingested-count" class="number">...</div>
                </div>
                <div class="card">
                    <h2>Processed Batches</h2>
                    <div id="processed-count" class="number">...</div>
                </div>
            </div>
            <div class="status" id="last-update">Updating...</div>

            <script>
                async function fetchMetrics() {
                    const response = await fetch('/metrics');
                    const data = await response.json();
                    document.getElementById('ingested-count').innerText = data.ingested_events_count;
                    document.getElementById('processed-count').innerText = data.processed_batches_count;
                    document.getElementById('last-update').innerText = "Last Updated: " + new Date(data.last_updated).toLocaleTimeString();
                }
                fetchMetrics();
                setInterval(fetchMetrics, 2000);
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
