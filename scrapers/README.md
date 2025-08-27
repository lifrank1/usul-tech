# SOF Week Speaker Scrapers

This directory contains all the web scraping tools for extracting speaker data from the SOF Week agenda.

## Files

### Main Scraper
- **`scraper.py`** - Production scraper with bio extraction and modal handling

### Utilities
- **`clean_speakers.py`** - Data cleaning and validation script

## Usage

### Run Background Scraper
```bash
# From main directory
./run_scraper.sh

# Monitor progress
tail -f scrapers/scraper.log

# Stop scraper
kill $(cat scrapers/scraper.pid)
```

### Run Scraper Directly
```bash
cd scrapers
python3 scraper.py
```

## Output

All scrapers save results to the main directory:
- `sof_week_speakers_complete.json` - Complete speaker data with bios
- `scrapers/scraper.log` - Detailed logging output

## Features

- **Profile Picture Clicking**: Automatically clicks speaker photos to extract detailed bios
- **Modal Detection**: Handles dynamic popup windows with biographical information
- **Timeout Protection**: Prevents hanging on problematic speakers
- **Background Processing**: Runs without blocking other work
- **Comprehensive Logging**: Detailed progress and error reporting
- **Duplicate Removal**: Intelligent deduplication of speaker records
