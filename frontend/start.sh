#!/bin/bash

echo "🚀 Starting SOF Week Frontend..."
echo "Make sure your backend is running on port 8000"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start the frontend
echo "🌐 Starting React development server..."
npm start
