#!/usr/bin/env python3
import json
import re
from datetime import datetime

def clean_speaker_data():
    """Clean and filter the scraped speaker data"""
    
    # Load the raw data
    with open('speakers_enhanced.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    raw_speakers = data['speakers']
    clean_speakers = []
    
    print(f"🔧 Cleaning {len(raw_speakers)} raw speaker entries...")
    
    for speaker in raw_speakers:
        name = speaker.get('name', '').strip()
        
        # Skip invalid entries
        if not name or name in ['&nbsp; &nbsp;', '']:
            continue
            
        # Skip entries that don't look like real names
        if (name.startswith('ms.') or 
            name.startswith('General Session') or
            name.startswith('Mayor of Tampa') or
            name.startswith('general session') or
            name.startswith('of Defense') or
            'This event' in name or
            'The portfolio' in name or
            'Enterprise Information' in name or
            'Much of' in name or
            'USSOCOM SOF' in name):
            continue
            
        # Clean up the name
        name = re.sub(r'&nbsp;', ' ', name).strip()
        name = re.sub(r'\s+', ' ', name)
        
        # Skip if still invalid
        if len(name) < 3 or not re.search(r'[A-Za-z]', name):
            continue
        
        # Clean other fields
        title = speaker.get('title', '').replace('&nbsp;', ' ').strip()
        company = speaker.get('company', '').replace('&nbsp;', ' ').strip()
        
        clean_speaker = {
            'name': name,
            'title': title,
            'company': company,
            'session_title': speaker.get('session_title', '').strip(),
            'speaking_time': speaker.get('speaking_time', '').strip(),
            'location': speaker.get('location', '').strip(),
            'session_description': speaker.get('session_description', '').strip(),
            'image_url': speaker.get('image_url', '').strip(),
            'extraction_method': speaker.get('extraction_method', 'unknown')
        }
        
        # Skip if we already have this speaker
        if any(existing['name'].lower() == name.lower() for existing in clean_speakers):
            continue
            
        clean_speakers.append(clean_speaker)
        print(f"✅ Kept: {name}")
    
    # Sort by name
    clean_speakers.sort(key=lambda x: x['name'])
    
    # Create final output
    final_data = {
        'scraped_at': datetime.now().isoformat(),
        'total_speakers': len(clean_speakers),
        'source_url': data['source_url'],
        'cvent_url': data['cvent_url'],
        'description': 'SOF Week 2025 Speaker List - Extracted from https://sofweek.org/agenda/',
        'speakers': clean_speakers
    }
    
    # Save cleaned data
    with open('sof_week_speakers_final.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎯 CLEANING COMPLETE!")
    print(f"📊 Final speaker count: {len(clean_speakers)}")
    print(f"💾 Saved to: sof_week_speakers_final.json")
    
    return clean_speakers

def print_summary(speakers):
    """Print a nice summary of the speakers"""
    print(f"\n{'='*80}")
    print(f"SOF WEEK 2025 SPEAKERS SUMMARY")
    print(f"{'='*80}")
    print(f"Total Speakers: {len(speakers)}")
    print(f"Scraped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    
    # Group by session/role
    keynote_speakers = []
    general_session_speakers = []
    panel_speakers = []
    other_speakers = []
    
    for speaker in speakers:
        session = speaker.get('session_title', '').lower()
        if 'keynote' in session:
            keynote_speakers.append(speaker)
        elif 'general session' in session:
            general_session_speakers.append(speaker)
        elif 'panel' in session:
            panel_speakers.append(speaker)
        else:
            other_speakers.append(speaker)
    
    def print_speaker_group(title, speaker_list):
        if speaker_list:
            print(f"\n{title}:")
            print("-" * len(title))
            for speaker in speaker_list:
                print(f"• {speaker['name']}")
                if speaker.get('title'):
                    print(f"  {speaker['title']}")
                if speaker.get('company'):
                    print(f"  {speaker['company']}")
                if speaker.get('speaking_time'):
                    print(f"  🕐 {speaker['speaking_time']}")
                print()
    
    print_speaker_group("KEYNOTE SPEAKERS", keynote_speakers)
    print_speaker_group("GENERAL SESSION SPEAKERS", general_session_speakers)
    print_speaker_group("PANEL SPEAKERS", panel_speakers)
    print_speaker_group("OTHER SPEAKERS", other_speakers)

if __name__ == "__main__":
    speakers = clean_speaker_data()
    print_summary(speakers)
