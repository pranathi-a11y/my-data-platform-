from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import os
import glob
import random

app = FastAPI(title="Data Platform Serving API")

# Mock data
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
    # Local metrics (works when producer is running on your Mac)
    raw_files = glob.glob("data_lake/raw/user_clicks/*.json")
    clean_files = glob.glob("data_lake/clean/user_clicks/*.parquet") + glob.glob("data_lake/clean/user_clicks/*.csv")
    
    # Generate some mock trend data for the graph
    now = datetime.now()
    labels = [(now - timedelta(minutes=i)).strftime("%H:%M") for i in range(10, 0, -1)]
    # Use real counts if available, otherwise mock a trend
    base_count = len(raw_files) if len(raw_files) > 0 else 50
    data_points = [base_count + random.randint(-5, 15) for _ in range(10)]
    
    return {
        "ingested_events_count": len(raw_files),
        "processed_batches_count": len(clean_files),
        "labels": labels,
        "data_points": data_points,
        "last_updated": now.isoformat()
    }

@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Data Platform Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body { font-family: 'Inter', -apple-system, sans-serif; background-color: #0f172a; color: white; display: flex; flex-direction: column; align-items: center; padding: 40px; margin: 0; }
                .header { text-align: center; margin-bottom: 40px; }
                .header h1 { font-size: 2.5rem; margin-bottom: 10px; background: linear-gradient(90deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
                .card-container { display: flex; gap: 20px; margin-bottom: 40px; width: 100%; max-width: 900px; }
                .card { background: #1e293b; padding: 25px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); text-align: center; flex: 1; border: 1px solid #334155; }
                .card h2 { color: #94a3b8; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; }
                .card .number { font-size: 3.5rem; font-weight: 800; color: #38bdf8; }
                .chart-container { background: #1e293b; padding: 30px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); width: 100%; max-width: 900px; border: 1px solid #334155; height: 400px; }
                .status-bar { margin-top: 30px; color: #64748b; font-size: 0.85rem; display: flex; align-items: center; gap: 8px; }
                .dot { height: 8px; width: 8px; background-color: #22c55e; border-radius: 50%; display: inline-block; animation: pulse 2s infinite; }
                @keyframes pulse { 0% { opacity: 0.4; } 50% { opacity: 1; } 100% { opacity: 0.4; } }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Data Platform Monitor</h1>
                <p>Real-time pipeline ingestion & processing trends</p>
            </div>
            
            <div class="card-container">
                <div class="card">
                    <h2>Live Ingested Events</h2>
                    <div id="ingested-count" class="number">0</div>
                </div>
                <div class="card">
                    <h2>Batches Cleaned</h2>
                    <div id="processed-count" class="number">0</div>
                </div>
            </div>

            <div class="chart-container">
                <canvas id="trendsChart"></canvas>
            </div>

            <div class="status-bar">
                <span class="dot"></span> <span id="last-update">Connecting to pipeline...</span>
            </div>

            <script>
                let myChart;
                async function updateDashboard() {
                    try {
                        const response = await fetch('/metrics');
                        const data = await response.json();
                        
                        document.getElementById('ingested-count').innerText = data.ingested_events_count;
                        document.getElementById('processed-count').innerText = data.processed_batches_count;
                        document.getElementById('last-update').innerText = "Live: Last Updated at " + new Date(data.last_updated).toLocaleTimeString();
                        
                        if (!myChart) {
                            const ctx = document.getElementById('trendsChart').getContext('2d');
                            myChart = new Chart(ctx, {
                                type: 'line',
                                data: {
                                    labels: data.labels,
                                    datasets: [{
                                        label: 'Ingestion Rate (events/sec)',
                                        data: data.data_points,
                                        borderColor: '#38bdf8',
                                        backgroundColor: 'rgba(56, 189, 248, 0.1)',
                                        fill: true,
                                        tension: 0.4,
                                        borderWidth: 3,
                                        pointRadius: 4,
                                        pointBackgroundColor: '#38bdf8'
                                    }]
                                },
                                options: {
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    plugins: { legend: { display: false } },
                                    scales: {
                                        y: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' }, beginAtZero: true },
                                        x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
                                    }
                                }
                            });
                        } else {
                            myChart.data.labels = data.labels;
                            myChart.data.datasets[0].data = data.data_points;
                            myChart.update('none');
                        }
                    } catch (e) {
                        console.error("Dashboard update failed", e);
                    }
                }
                
                setInterval(updateDashboard, 2000);
                updateDashboard();
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
