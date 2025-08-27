#!/usr/bin/env python3
import asyncio
import json
import re
from playwright.async_api import async_playwright
from datetime import datetime
from bs4 import BeautifulSoup

class EnhancedSOFScraper:
    def __init__(self):
        self.base_url = "https://sofweek.org/agenda/"
        self.cvent_url = "https://event-guestside-app-pr50.cvent-production.cvent.cloud/embedded-agenda/461ba942-5adb-45cf-a9e5-e8e40dd9305c"
        self.speakers_data = []

    async def scrape_speakers(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            try:
                print("🌐 Loading SOF Week agenda...")
                await page.goto(self.cvent_url, wait_until="domcontentloaded", timeout=45000)
                await page.wait_for_timeout(10000)  # Wait for dynamic content
                
                content = await page.content()
                print(f"📄 Loaded {len(content)} characters of content")
                
                # Parse with BeautifulSoup for better HTML handling
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract speakers from speaker cards
                await self.extract_speaker_cards(soup, page)
                
                # Extract additional speakers from session descriptions
                await self.extract_speakers_from_sessions(soup)
                
                # Remove duplicates
                self.remove_duplicates()
                
            except Exception as e:
                print(f"❌ Error during scraping: {e}")
                
            finally:
                await browser.close()
        
        return self.speakers_data

    async def extract_speaker_cards(self, soup, page):
        """Extract speakers from dedicated speaker card elements"""
        print("🔍 Looking for speaker cards...")
        
        # Find all speaker cards
        speaker_cards = soup.find_all('div', {'class': re.compile(r'.*speakerCard.*')})
        print(f"Found {len(speaker_cards)} speaker cards")
        
        for card in speaker_cards:
            try:
                speaker_info = {}
                
                # Extract name
                name_elem = card.find('div', {'data-cvent-id': 'speaker-name'})
                if name_elem:
                    speaker_info['name'] = name_elem.get_text(strip=True)
                    
                # Extract title
                title_elem = card.find('div', {'data-cvent-id': 'speaker-card-speaker-info-speaker-title'})
                if title_elem:
                    speaker_info['title'] = title_elem.get_text(strip=True)
                    
                # Extract company
                company_elem = card.find('div', {'data-cvent-id': 'speaker-card-speaker-info-speaker-company'})
                if company_elem:
                    speaker_info['company'] = company_elem.get_text(strip=True)
                    
                # Extract image URL
                img_elem = card.find('img', {'data-cvent-id': 'speaker-card-user-profile-image'})
                if img_elem and img_elem.get('src'):
                    speaker_info['image_url'] = img_elem.get('src')
                
                # Find associated session information
                session_info = self.find_associated_session(card, soup)
                if session_info:
                    speaker_info.update(session_info)
                
                if speaker_info.get('name'):
                    speaker_info['extraction_method'] = 'speaker_card'
                    self.speakers_data.append(speaker_info)
                    print(f"✅ Added speaker: {speaker_info['name']}")
                    
            except Exception as e:
                print(f"⚠️ Error processing speaker card: {e}")
                continue

    def find_associated_session(self, speaker_card, soup):
        """Find session information associated with a speaker"""
        session_info = {}
        
        # Look for parent session container
        session_container = speaker_card.find_parent('div', {'data-cvent-id': 'agenda-v2-widget-session-tile-card'})
        
        if session_container:
            # Extract session name
            session_name_elem = session_container.find('div', {'data-cvent-id': 'session-tile-card-session-name'})
            if session_name_elem:
                session_info['session_title'] = session_name_elem.get_text(strip=True)
            
            # Extract session time
            session_time_elem = session_container.find('div', {'data-cvent-id': 'session-tile-card-session-time'})
            if session_time_elem:
                time_text = session_time_elem.get_text(strip=True)
                session_info['speaking_time'] = time_text
            
            # Extract session location
            location_elem = session_container.find('div', {'data-cvent-id': 'session-list-card-session-location'})
            if location_elem:
                session_info['location'] = location_elem.get_text(strip=True)
                
            # Extract session description
            desc_elem = session_container.find('div', {'data-cvent-id': 'session-tile-card-session-description'})
            if desc_elem:
                desc_text = desc_elem.get_text(strip=True)
                session_info['session_description'] = desc_text[:500] + "..." if len(desc_text) > 500 else desc_text
        
        return session_info

    async def extract_speakers_from_sessions(self, soup):
        """Extract additional speaker mentions from session descriptions and titles"""
        print("🔍 Looking for additional speakers in session content...")
        
        # Find all session elements
        sessions = soup.find_all('div', {'data-cvent-id': 'agenda-v2-widget-session-tile-card'})
        
        for session in sessions:
            try:
                # Get session details
                session_name_elem = session.find('div', {'data-cvent-id': 'session-tile-card-session-name'})
                session_time_elem = session.find('div', {'data-cvent-id': 'session-tile-card-session-time'})
                location_elem = session.find('div', {'data-cvent-id': 'session-list-card-session-location'})
                desc_elem = session.find('div', {'data-cvent-id': 'session-tile-card-session-description'})
                
                session_title = session_name_elem.get_text(strip=True) if session_name_elem else ""
                session_time = session_time_elem.get_text(strip=True) if session_time_elem else ""
                location = location_elem.get_text(strip=True) if location_elem else ""
                description = desc_elem.get_text(strip=True) if desc_elem else ""
                
                # Combine all text for speaker extraction
                full_text = f"{session_title} {description}"
                
                # Look for speaker name patterns
                speaker_patterns = [
                    r'((?:Mr\.|Ms\.|Dr\.|General|Admiral|Colonel|Lieutenant|The Honorable|Mayor|Command Sergeant Major)\s+[A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
                    r'(Jeff\s+Pottinger|Matt\s+Stevens)',
                    r'Secretary\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
                    r'Commander\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
                ]
                
                for pattern in speaker_patterns:
                    matches = re.finditer(pattern, full_text, re.IGNORECASE)
                    for match in matches:
                        name = match.group(1).strip() if match.lastindex and match.lastindex >= 1 else match.group(0).strip()
                        
                        # Skip if already exists
                        if any(existing['name'].lower() == name.lower() for existing in self.speakers_data):
                            continue
                            
                        speaker_info = {
                            'name': name,
                            'title': '',
                            'company': '',
                            'session_title': session_title,
                            'speaking_time': session_time,
                            'location': location,
                            'session_description': description[:300] + "..." if len(description) > 300 else description,
                            'extraction_method': 'session_content',
                            'image_url': ''
                        }
                        
                        # Try to extract title and company from surrounding text
                        self.enhance_speaker_info(speaker_info, full_text, name)
                        
                        self.speakers_data.append(speaker_info)
                        print(f"✅ Found additional speaker: {name}")
                        
            except Exception as e:
                print(f"⚠️ Error processing session: {e}")
                continue

    def enhance_speaker_info(self, speaker_info, text, name):
        """Try to extract additional information about a speaker from text"""
        # Look for title patterns near the name
        name_pos = text.lower().find(name.lower())
        if name_pos == -1:
            return
            
        # Get context around the name (200 chars before and after)
        start = max(0, name_pos - 200)
        end = min(len(text), name_pos + len(name) + 200)
        context = text[start:end]
        
        # Title patterns
        title_patterns = [
            r'Secretary\s+of\s+Defense',
            r'Commander',
            r'Senior\s+Enlisted\s+Leader',
            r'Mayor',
            r'Former\s+Deputy\s+Assistant\s+Secretary\s+of\s+Defense',
            r'CAPTAIN,\s+USN\s+\(Ret\.\)',
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                speaker_info['title'] = match.group(0)
                break
        
        # Company patterns
        company_patterns = [
            r'U\.S\.\s+Department\s+of\s+Defense',
            r'U\.S\.\s+Special\s+Operations\s+Command',
            r'City\s+of\s+Tampa',
            r'Global\s+SOF\s+Advisory\s+Board',
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                speaker_info['company'] = match.group(0)
                break

    def remove_duplicates(self):
        """Remove duplicate speakers based on name similarity"""
        unique_speakers = []
        seen_names = set()
        
        for speaker in self.speakers_data:
            name_key = re.sub(r'[^\w\s]', '', speaker['name'].lower()).strip()
            if name_key not in seen_names:
                seen_names.add(name_key)
                unique_speakers.append(speaker)
            else:
                # If duplicate, merge information from the more complete record
                existing = next(s for s in unique_speakers if re.sub(r'[^\w\s]', '', s['name'].lower()).strip() == name_key)
                self.merge_speaker_info(existing, speaker)
        
        self.speakers_data = unique_speakers
        print(f"🔄 After deduplication: {len(self.speakers_data)} unique speakers")

    def merge_speaker_info(self, existing, new):
        """Merge information from two speaker records"""
        # Prefer non-empty values
        for key in ['title', 'company', 'session_title', 'speaking_time', 'location', 'session_description', 'image_url']:
            if not existing.get(key) and new.get(key):
                existing[key] = new[key]
            elif existing.get(key) and new.get(key) and len(new[key]) > len(existing[key]):
                existing[key] = new[key]

    def save_to_json(self, filename="speakers_enhanced.json"):
        """Save speakers data to JSON file"""
        try:
            output_data = {
                'scraped_at': datetime.now().isoformat(),
                'total_speakers': len(self.speakers_data),
                'source_url': self.base_url,
                'cvent_url': self.cvent_url,
                'speakers': self.speakers_data
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved {len(self.speakers_data)} speakers to {filename}")
            
        except Exception as e:
            print(f"❌ Error saving to JSON: {e}")

async def main():
    scraper = EnhancedSOFScraper()
    speakers = await scraper.scrape_speakers()
    
    print(f"\n🎯 SCRAPING COMPLETE!")
    print(f"📊 Total speakers found: {len(speakers)}")
    
    if speakers:
        print("\n👥 SPEAKERS FOUND:")
        for i, speaker in enumerate(speakers, 1):
            print(f"\n{i}. {speaker['name']}")
            if speaker.get('title'):
                print(f"   📋 Title: {speaker['title']}")
            if speaker.get('company'):
                print(f"   🏢 Company: {speaker['company']}")
            if speaker.get('session_title'):
                print(f"   🎤 Session: {speaker['session_title']}")
            if speaker.get('speaking_time'):
                print(f"   ⏰ Time: {speaker['speaking_time']}")
            if speaker.get('location'):
                print(f"   📍 Location: {speaker['location']}")
            print(f"   🔧 Method: {speaker.get('extraction_method', 'unknown')}")
    
    scraper.save_to_json()
    return speakers

if __name__ == "__main__":
    asyncio.run(main())
