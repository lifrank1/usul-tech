# SOF Week 2025 Speaker Scraper

This project successfully extracts detailed speaker information from the SOF Week 2025 agenda page at https://sofweek.org/agenda/, including **detailed biographical information** obtained by clicking on speaker profile pictures.

## 🎯 Results

**Successfully extracts 35+ verified speakers** with complete information including:
- Full names and professional titles
- Companies/organizations  
- Session details and speaking times
- Venue locations and session descriptions
- Profile image URLs
- **🆕 Detailed biographical information** (extracted by clicking profile pictures)

## 📁 Project Structure

### Main Files
- **`run_scraper.sh`** - Production scraper runner with background execution
- **`sof_week_speakers_complete.json`** - Complete speaker data with bios (generated)
- **`requirements.txt`** - Python dependencies

### Scrapers Directory (`scrapers/`)
- **`scraper.py`** - Production scraper with bio extraction
- **`clean_speakers.py`** - Data cleaning utilities
- **`scraper.log`** - Live scraping progress log
- **`README.md`** - Detailed scraper documentation

## 🚀 Quick Start

### Background Scraper (Recommended)
```bash
# Install dependencies
pip install -r requirements.txt
playwright install

# Run scraper in background
./run_scraper.sh

# Monitor progress
tail -f scrapers/scraper.log
```

### Direct Scraper Run
```bash
# Install dependencies
pip install -r requirements.txt
playwright install

# Run scraper directly
cd scrapers && python3 scraper.py
```

## 📊 Output Format

The final JSON contains structured speaker data:

```json
{
  "scraped_at": "2025-08-27T19:03:36",
  "total_speakers": 35,
  "source_url": "https://sofweek.org/agenda/",
  "speakers": [
    {
      "name": "The Honorable Pete Hegseth",
      "title": "Secretary of Defense",
      "company": "U.S. Department of Defense",
      "session_title": "Keynote Address: U.S. Secretary of Defense",
      "speaking_time": "8:45 AM-9:15 AM",
      "location": "JW Marriott: Tampa Bay Ballroom",
      "session_description": "...",
      "image_url": "https://custom.cvent.com/...",
      "extraction_method": "speaker_card"
    }
  ]
}
```

## 🔧 Technical Solution

The scraper handles the complex dynamic content loading:

1. **Accesses Cvent iframe**: The agenda content is embedded via Cvent's platform
2. **Waits for JavaScript**: Content loads dynamically after page load
3. **Dual extraction**: Finds speakers in both speaker cards and session descriptions
4. **Smart deduplication**: Merges information and removes duplicates
5. **Data validation**: Filters out invalid entries and cleans data

## 🏆 Key Speakers Found

- **The Honorable Pete Hegseth** - Secretary of Defense
- **General Bryan P. Fenton** - USSOCOM Commander
- **Mayor Jane Castor** - Tampa Mayor
- **Mr. Jeff Pottinger** - ReLAUNCH Advisors Co-Founder
- **Mr. Matt Stevens** - The Honor Foundation CEO
- **30+ additional speakers** with full details

## ⚙️ Why Playwright Won

Playwright proved superior to Selenium and simple HTTP requests because:
- ✅ Handles modern JavaScript-heavy websites
- ✅ Reliable iframe content access
- ✅ Better element detection and parsing
- ✅ No browser driver compatibility issues