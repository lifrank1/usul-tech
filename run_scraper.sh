#!/bin/bash

# SOF Week Speaker Scraper - Production Version
# Extracts all speakers with detailed bios from profile pictures

echo "🚀 Starting SOF Week speaker scraper..."
echo "📅 Started at: $(date)"
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

echo "✅ Background scraper started with PID: $SCRAPER_PID"
echo "📊 To monitor progress: tail -f scrapers/scraper.log"
echo "🛑 To stop the scraper: kill $SCRAPER_PID"
echo ""
echo "✨ FEATURES:"
echo "   - Clicks speaker profile pictures to extract detailed bios"
echo "   - Handles modal dialogs and timeouts gracefully"
echo "   - Comprehensive logging and error handling"
echo "   - Automatic duplicate removal and data cleaning"
echo ""
echo "You can now continue working while the scraper runs in background!"

# Save PID to file
echo $SCRAPER_PID > scraper.pid

# Show initial log output
echo "📝 Initial log output:"
sleep 3
tail -n 15 scraper.log 2>/dev/null || echo "   (Log file will appear once scraper starts)"
