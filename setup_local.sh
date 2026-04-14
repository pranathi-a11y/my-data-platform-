#!/bin/bash

echo "🚀 Starting Local Data Platform Setup (No Docker)..."

# 1. Clean up old venv
if [ -d "venv" ]; then
    echo "🧹 Cleaning up old virtual environment..."
    rm -rf venv
fi

# 2. Create fresh venv
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 3. Install simplified dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Create local data lake directories
echo "📁 Creating data lake folders..."
mkdir -p data_lake/raw/user_clicks
mkdir -p data_lake/clean/user_clicks
mkdir -p data_lake/analytics

echo "✅ Setup complete! To start, run: source venv/bin/activate"
