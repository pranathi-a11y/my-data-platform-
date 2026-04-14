from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
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
    return RedirectResponse(url="/dashboard")

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
    raw_files = glob.glob("data_lake/raw/user_clicks/*.json")
    clean_files = glob.glob("data_lake/clean/user_clicks/*.parquet") + glob.glob("data_lake/clean/user_clicks/*.csv")
    
    now = datetime.now()
    labels = [(now - timedelta(minutes=i)).strftime("%H:%M") for i in range(10, 0, -1)]
    base_count = len(raw_files) if len(raw_files) > 0 else 50
    data_points = [base_count + random.randint(-5, 15) for _ in range(10)]
    
    # Simulate processing rate
    proc_points = [int(p * 0.8) + random.randint(-2, 5) for p in data_points]
    
    return {
        "ingested_events_count": len(raw_files),
        "processed_batches_count": len(clean_files),
        "labels": labels,
        "data_points": data_points,
        "proc_points": proc_points,
        "last_updated": now.isoformat(),
        "system_health": random.randint(95, 100),
        "latency": random.randint(12, 45)
    }

@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CloudData | Platform Monitor</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #020617; color: #f8fafc; }
            .glass-card { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
            .glass-card:hover { border-color: #38bdf8; transform: translateY(-2px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5); }
            .gradient-text { background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
            .status-glow { box-shadow: 0 0 15px rgba(34, 197, 94, 0.4); }
            @keyframes pulse-slow { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(0.95); } }
            .animate-pulse-slow { animation: pulse-slow 3s infinite; }
            ::-webkit-scrollbar { width: 8px; }
            ::-webkit-scrollbar-track { background: #020617; }
            ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 4px; }
            ::-webkit-scrollbar-thumb:hover { background: #334155; }
        </style>
    </head>
    <body class="min-h-screen p-4 md:p-8">
        <div class="max-w-7xl mx-auto">
            <!-- Header -->
            <header class="flex flex-col md:flex-row justify-between items-center mb-12 gap-6">
                <div>
                    <h1 class="text-4xl font-extrabold gradient-text tracking-tight mb-2">CloudData OS</h1>
                    <p class="text-slate-400 font-medium">Real-time 5-Layer Data Platform Orchestrator</p>
                </div>
                <div class="flex items-center gap-4 bg-slate-900/50 p-2 rounded-2xl border border-slate-800">
                    <div class="flex items-center gap-2 px-4 py-2 bg-emerald-500/10 text-emerald-400 rounded-xl border border-emerald-500/20">
                        <div class="h-2 w-2 rounded-full bg-emerald-500 animate-pulse status-glow"></div>
                        <span class="text-sm font-bold uppercase tracking-wider">System Live</span>
                    </div>
                    <div class="text-slate-500 text-sm font-mono px-4" id="clock">00:00:00</div>
                </div>
            </header>

            <!-- Stats Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <div class="glass-card p-6 rounded-3xl">
                    <p class="text-slate-400 text-sm font-bold uppercase tracking-widest mb-4">Total Ingested</p>
                    <div class="flex items-baseline gap-2">
                        <span id="ingested-count" class="text-5xl font-extrabold text-white">0</span>
                        <span class="text-sky-400 text-sm font-bold">events</span>
                    </div>
                </div>
                <div class="glass-card p-6 rounded-3xl">
                    <p class="text-slate-400 text-sm font-bold uppercase tracking-widest mb-4">Batches Cleaned</p>
                    <div class="flex items-baseline gap-2">
                        <span id="processed-count" class="text-5xl font-extrabold text-white">0</span>
                        <span class="text-indigo-400 text-sm font-bold">batches</span>
                    </div>
                </div>
                <div class="glass-card p-6 rounded-3xl border-l-4 border-l-emerald-500">
                    <p class="text-slate-400 text-sm font-bold uppercase tracking-widest mb-4">Uptime Health</p>
                    <div class="flex items-baseline gap-2">
                        <span id="health-pct" class="text-5xl font-extrabold text-emerald-400">99</span>
                        <span class="text-emerald-500 text-sm font-bold">%</span>
                    </div>
                </div>
                <div class="glass-card p-6 rounded-3xl">
                    <p class="text-slate-400 text-sm font-bold uppercase tracking-widest mb-4">Avg Latency</p>
                    <div class="flex items-baseline gap-2">
                        <span id="latency-val" class="text-5xl font-extrabold text-sky-400">24</span>
                        <span class="text-sky-500 text-sm font-bold">ms</span>
                    </div>
                </div>
            </div>

            <!-- Charts Section -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
                <div class="glass-card p-8 rounded-3xl lg:col-span-2">
                    <div class="flex justify-between items-center mb-8">
                        <h3 class="text-xl font-bold text-white">Ingestion vs Processing Rate</h3>
                        <div class="flex gap-4">
                            <div class="flex items-center gap-2">
                                <div class="h-3 w-3 rounded-full bg-sky-500"></div>
                                <span class="text-xs text-slate-400 font-bold uppercase">Ingested</span>
                            </div>
                            <div class="flex items-center gap-2">
                                <div class="h-3 w-3 rounded-full bg-indigo-500"></div>
                                <span class="text-xs text-slate-400 font-bold uppercase">Processed</span>
                            </div>
                        </div>
                    </div>
                    <div class="h-[350px]">
                        <canvas id="mainChart"></canvas>
                    </div>
                </div>
                <div class="glass-card p-8 rounded-3xl">
                    <h3 class="text-xl font-bold text-white mb-8">Platform Health</h3>
                    <div class="h-[350px] flex items-center justify-center relative">
                        <canvas id="healthChart"></canvas>
                        <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                            <span class="text-4xl font-extrabold text-white" id="health-donut-val">98%</span>
                            <span class="text-xs text-slate-500 font-bold uppercase">Optimal</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Footer Status -->
            <footer class="flex flex-col md:flex-row justify-between items-center py-6 border-t border-slate-800/50 gap-4">
                <div class="flex items-center gap-3 text-slate-500 text-sm">
                    <span id="last-update">Syncing with pipeline...</span>
                </div>
                <div class="flex items-center gap-6">
                    <a href="/docs" class="text-slate-400 hover:text-sky-400 text-sm font-bold transition-colors">API Reference</a>
                    <a href="/health" class="text-slate-400 hover:text-sky-400 text-sm font-bold transition-colors">System Health</a>
                </div>
            </footer>
        </div>

        <script>
            let mainChart, healthChart;

            function updateClock() {
                const now = new Date();
                document.getElementById('clock').innerText = now.toLocaleTimeString('en-US', { hour12: false });
            }
            setInterval(updateClock, 1000);
            updateClock();

            async function updateData() {
                try {
                    const res = await fetch('/metrics');
                    const data = await res.json();

                    document.getElementById('ingested-count').innerText = data.ingested_events_count;
                    document.getElementById('processed-count').innerText = data.processed_batches_count;
                    document.getElementById('health-pct').innerText = data.system_health;
                    document.getElementById('health-donut-val').innerText = data.system_health + '%';
                    document.getElementById('latency-val').innerText = data.latency;
                    document.getElementById('last-update').innerText = "Last Sync: " + new Date(data.last_updated).toLocaleTimeString();

                    if (!mainChart) {
                        const ctx = document.getElementById('mainChart').getContext('2d');
                        mainChart = new Chart(ctx, {
                            type: 'line',
                            data: {
                                labels: data.labels,
                                datasets: [{
                                    label: 'Ingested',
                                    data: data.data_points,
                                    borderColor: '#38bdf8',
                                    backgroundColor: 'rgba(56, 189, 248, 0.05)',
                                    fill: true,
                                    tension: 0.4,
                                    borderWidth: 4,
                                    pointRadius: 0,
                                    pointHitRadius: 20
                                }, {
                                    label: 'Processed',
                                    data: data.proc_points,
                                    borderColor: '#818cf8',
                                    backgroundColor: 'rgba(129, 140, 248, 0.05)',
                                    fill: true,
                                    tension: 0.4,
                                    borderWidth: 4,
                                    pointRadius: 0,
                                    pointHitRadius: 20
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: { legend: { display: false } },
                                scales: {
                                    y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#64748b', font: { weight: '600' } } },
                                    x: { grid: { display: false }, ticks: { color: '#64748b', font: { weight: '600' } } }
                                }
                            }
                        });

                        const hCtx = document.getElementById('healthChart').getContext('2d');
                        healthChart = new Chart(hCtx, {
                            type: 'doughnut',
                            data: {
                                datasets: [{
                                    data: [data.system_health, 100 - data.system_health],
                                    backgroundColor: ['#10b981', '#1e293b'],
                                    borderWidth: 0,
                                    cutout: '85%'
                                }]
                            },
                            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
                        });
                    } else {
                        mainChart.data.labels = data.labels;
                        mainChart.data.datasets[0].data = data.data_points;
                        mainChart.data.datasets[1].data = data.proc_points;
                        mainChart.update('none');

                        healthChart.data.datasets[0].data = [data.system_health, 100 - data.system_health];
                        healthChart.update('none');
                    }
                } catch (e) { console.error(e); }
            }

            setInterval(updateData, 2000);
            updateData();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
