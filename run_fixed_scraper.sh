#!/bin/bash

# SOF Week Speaker Scraper - FIXED VERSION
# This version properly handles modal closing to prevent interference

echo "🔧 Starting FIXED SOF Week speaker scraper..."
echo "📅 Started at: $(date)"
echo "🐛 This version fixes the modal interference issue"
echo "📋 Progress will be logged to: scrapers/scraper.log"
echo "📄 Results will be saved to: sof_week_speakers_complete.json"
echo ""

# Change to scrapers directory and run the FIXED scraper in background
cd scrapers

# Clear old log
> scraper.log

# Run the production scraper in background
nohup python3 scraper.py > scraper_output.log 2>&1 &

# Get the process ID
SCRAPER_PID=$!

echo "✅ FIXED background scraper started with PID: $SCRAPER_PID"
echo "📊 To monitor progress: tail -f scrapers/scraper.log"
echo "🛑 To stop the scraper: kill $SCRAPER_PID"
echo ""
echo "🔧 FIXES APPLIED:"
echo "   - Aggressive modal closing before each speaker"
echo "   - Force close all modals after each attempt"
echo "   - JavaScript modal removal"
echo "   - Better error handling and timeouts"
echo ""
echo "You can now continue working while the FIXED scraper runs!"

# Save PID to file
echo $SCRAPER_PID > scraper.pid

# Show initial log output
echo "📝 Initial log output:"
sleep 3
tail -n 15 scraper.log 2>/dev/null || echo "   (Log file will appear once scraper starts)"
