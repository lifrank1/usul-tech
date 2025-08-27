#!/usr/bin/env python3
import asyncio
import json
import re
import sys
import os
from datetime import datetime
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FixedBackgroundSOFScraper:
    def __init__(self):
        self.base_url = "https://sofweek.org/agenda/"
        self.cvent_url = "https://event-guestside-app-pr50.cvent-production.cvent.cloud/embedded-agenda/461ba942-5adb-45cf-a9e5-e8e40dd9305c"
        self.speakers_data = []
        self.successful_bios = 0
        self.processed_speakers = 0

    async def scrape_speakers(self):
        browser = None
        try:
            async with async_playwright() as p:
                logger.info("🚀 Starting FIXED background SOF Week speaker scraping...")
                
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-web-security']
                )
                page = await browser.new_page()
                
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                
                logger.info("🌐 Loading SOF Week agenda...")
                await page.goto(self.cvent_url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(15000)  # Wait for dynamic content
                
                content = await page.content()
                logger.info(f"📄 Loaded {len(content)} characters of content")
                
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract speakers with PROPER modal handling
                await self.extract_speakers_with_proper_modal_handling(soup, page)
                
                # Extract additional speakers from session descriptions
                await self.extract_speakers_from_sessions(soup)
                
                # Remove duplicates
                self.remove_duplicates()
                
                logger.info(f"🎯 Scraping completed! Found {len(self.speakers_data)} speakers, {self.successful_bios} with detailed bios")
                
        except Exception as e:
            logger.error(f"❌ Error during scraping: {e}")
            
        finally:
            if browser:
                try:
                    await browser.close()
                except:
                    pass
        
        return self.speakers_data

    async def extract_speakers_with_proper_modal_handling(self, soup, page):
        """Extract speakers with PROPER modal closing to prevent interference"""
        speaker_cards = soup.find_all('div', {'class': re.compile(r'.*speakerCard.*')})
        logger.info(f"🔍 Found {len(speaker_cards)} speaker cards to process")
        
        for i, card in enumerate(speaker_cards):
            try:
                # Extract basic info
                name_elem = card.find('div', {'data-cvent-id': 'speaker-name'})
                if not name_elem:
                    continue
                    
                speaker_name = name_elem.get_text(strip=True)
                if not speaker_name or speaker_name in ['&nbsp; &nbsp;', '', '&nbsp;']:
                    continue
                
                speaker_info = {
                    'name': speaker_name,
                    'title': self.safe_extract_text(card, 'speaker-card-speaker-info-speaker-title'),
                    'company': self.safe_extract_text(card, 'speaker-card-speaker-info-speaker-company'),
                    'image_url': self.safe_extract_image(card),
                    'detailed_bio': '',
                    'extraction_method': 'speaker_card_with_fixed_bio'
                }
                
                # Add session info
                session_info = self.find_associated_session(card, soup)
                speaker_info.update(session_info or {
                    'session_title': '', 'speaking_time': '', 
                    'location': '', 'session_description': ''
                })
                
                # CRITICAL: Ensure no modals are open before attempting bio extraction
                logger.info(f"🖱️ [{i+1}/{len(speaker_cards)}] Attempting bio extraction for: {speaker_name}")
                
                # Force close any existing modals FIRST
                await self.force_close_all_modals(page)
                await page.wait_for_timeout(1000)  # Wait for modals to close
                
                try:
                    bio = await asyncio.wait_for(
                        self.click_and_extract_bio_fixed(page, speaker_name, i),
                        timeout=25  # Reduced timeout
                    )
                    if bio and len(bio.strip()) > 50:
                        speaker_info['detailed_bio'] = bio
                        self.successful_bios += 1
                        logger.info(f"  ✅ Got bio ({len(bio)} chars)")
                    else:
                        logger.info(f"  ⚠️ No bio found")
                        
                except asyncio.TimeoutError:
                    logger.warning(f"  ⏰ Bio extraction timeout for {speaker_name}")
                except Exception as bio_error:
                    logger.warning(f"  ⚠️ Bio extraction error for {speaker_name}: {bio_error}")
                
                # CRITICAL: Force close modals after each attempt
                await self.force_close_all_modals(page)
                await page.wait_for_timeout(500)  # Brief pause
                
                self.speakers_data.append(speaker_info)
                self.processed_speakers += 1
                
            except Exception as e:
                logger.error(f"⚠️ Error processing speaker {i}: {e}")
                continue

    async def force_close_all_modals(self, page):
        """Aggressively close ALL modals to prevent interference"""
        try:
            # Strategy 1: Press Escape multiple times
            for _ in range(3):
                await page.keyboard.press('Escape')
                await page.wait_for_timeout(200)
            
            # Strategy 2: Click all possible close buttons
            close_selectors = [
                'button:has-text("Close")',
                'button:has-text("×")',
                '[aria-label="Close"]',
                '[data-testid*="close"]',
                '[data-cvent-id*="close"]',
                '.close',
                '[role="button"]:has-text("×")',
                'button[class*="close"]',
                '[class*="close-button"]'
            ]
            
            for selector in close_selectors:
                try:
                    close_buttons = page.locator(selector)
                    count = await close_buttons.count()
                    for i in range(count):
                        try:
                            await close_buttons.nth(i).click(timeout=1000)
                        except:
                            pass
                except:
                    continue
            
            # Strategy 3: Click outside any potential modal areas
            try:
                await page.click('body', position={'x': 10, 'y': 10}, timeout=1000)
            except:
                pass
                
            # Strategy 4: Remove modal elements directly via JavaScript
            await page.evaluate("""
                () => {
                    // Remove modal overlays
                    const modals = document.querySelectorAll('[role="dialog"], .modal, [class*="modal"], [data-cvent-id*="modal"]');
                    modals.forEach(modal => {
                        if (modal && modal.parentNode) {
                            modal.style.display = 'none';
                        }
                    });
                    
                    // Remove overlay backgrounds
                    const overlays = document.querySelectorAll('[class*="overlay"], [class*="backdrop"]');
                    overlays.forEach(overlay => {
                        if (overlay && overlay.parentNode) {
                            overlay.style.display = 'none';
                        }
                    });
                }
            """)
            
        except Exception as e:
            logger.debug(f"    Modal closing error: {e}")

    async def click_and_extract_bio_fixed(self, page, speaker_name, card_index):
        """Fixed bio extraction with aggressive modal management"""
        try:
            # Wait and ensure clean state
            await page.wait_for_timeout(1000)
            
            # Try clicking profile image
            profile_images = page.locator('[data-cvent-id="speaker-card-speaker-profile-image"]')
            if card_index < await profile_images.count():
                profile_image = profile_images.nth(card_index)
                
                try:
                    # Scroll element into view first
                    await profile_image.scroll_into_view_if_needed()
                    await page.wait_for_timeout(500)
                    
                    # Click with force if needed
                    await profile_image.click(force=True, timeout=5000)
                    logger.info(f"    🖱️ Clicked profile image")
                    
                    # Wait for modal to appear
                    await page.wait_for_timeout(3000)
                    
                    # Extract bio
                    bio = await self.extract_bio_from_modal_improved(page)
                    if bio:
                        logger.info(f"    📖 Extracted bio from modal")
                        return bio
                        
                except Exception as click_error:
                    logger.debug(f"    Profile image click failed: {click_error}")
            
            # Try clicking speaker name as backup
            speaker_names = page.locator('[data-cvent-id="speaker-name"]')
            if card_index < await speaker_names.count():
                speaker_name_elem = speaker_names.nth(card_index)
                
                try:
                    await speaker_name_elem.scroll_into_view_if_needed()
                    await page.wait_for_timeout(500)
                    await speaker_name_elem.click(force=True, timeout=5000)
                    logger.info(f"    🖱️ Clicked speaker name")
                    
                    await page.wait_for_timeout(3000)
                    bio = await self.extract_bio_from_modal_improved(page)
                    if bio:
                        logger.info(f"    📖 Extracted bio from name click")
                        return bio
                        
                except Exception as click_error:
                    logger.debug(f"    Speaker name click failed: {click_error}")
                    
        except Exception as e:
            logger.debug(f"    Bio extraction error: {e}")
            
        return None

    async def extract_bio_from_modal_improved(self, page):
        """Improved modal bio extraction with multiple strategies"""
        try:
            # Wait for modal content to load
            await page.wait_for_timeout(2000)
            
            # Strategy 1: Look for speaker detail modal specifically
            modal_selectors = [
                '[data-cvent-id="speaker-detail-modal"]',
                '[role="dialog"]',
                '.modal',
                '[class*="modal"]',
                '[aria-modal="true"]'
            ]
            
            for selector in modal_selectors:
                try:
                    modal = page.locator(selector).first
                    if await modal.count() > 0:
                        # Check if modal is visible
                        is_visible = await modal.is_visible()
                        if is_visible:
                            logger.info(f"    ✅ Found visible modal: {selector}")
                            
                            # Get all text content
                            modal_text = await modal.text_content()
                            if modal_text and len(modal_text.strip()) > 100:
                                bio = self.clean_bio_text(modal_text)
                                if len(bio) > 100:
                                    logger.info(f"    📖 Extracted {len(bio)} chars from modal text")
                                    return bio
                            
                            # Also try getting inner HTML for better parsing
                            modal_html = await modal.inner_html()
                            if modal_html:
                                soup = BeautifulSoup(modal_html, 'html.parser')
                                
                                # Look for paragraphs with substantial content
                                paragraphs = soup.find_all(['p', 'div'], string=re.compile(r'.{100,}'))
                                for para in paragraphs:
                                    text = para.get_text(strip=True)
                                    if len(text) > 100 and not any(skip in text.lower() for skip in ['close', 'cancel', 'back']):
                                        bio = self.clean_bio_text(text)
                                        if len(bio) > 100:
                                            logger.info(f"    📖 Extracted {len(bio)} chars from modal HTML")
                                            return bio
                                            
                except Exception as e:
                    logger.debug(f"    Modal selector {selector} failed: {e}")
                    continue
            
            # Strategy 2: Look for any new content that appeared
            try:
                # Check for any element containing biographical keywords
                bio_locator = page.locator('text=/.*\\b(experience|career|background|served|graduated|joined|director|officer|manager|years)\\b.*/i').first
                if await bio_locator.count() > 0:
                    bio_text = await bio_locator.text_content()
                    if bio_text and len(bio_text) > 100:
                        bio = self.clean_bio_text(bio_text)
                        if len(bio) > 100:
                            logger.info(f"    📖 Found bio content via keyword search")
                            return bio
            except:
                pass
                        
        except Exception as e:
            logger.debug(f"    Modal extraction error: {e}")
            
        return None

    def clean_bio_text(self, text):
        """Clean and format bio text"""
        if not text:
            return ""
            
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove modal UI text
        text = re.sub(r'\b(Close|Cancel|Back|×)\b.*?$', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^.*?(Close|Cancel|Back|×)\b', '', text, flags=re.IGNORECASE)
        
        # Remove common non-bio text
        text = re.sub(r'^.*?(Speaker|Profile|Biography|Bio)\s*:?\s*', '', text, flags=re.IGNORECASE)
        
        # Trim and limit
        text = text.strip()
        if len(text) > 1500:
            text = text[:1500] + "..."
            
        return text

    def safe_extract_text(self, card, data_id):
        """Safely extract text from card element"""
        try:
            elem = card.find('div', {'data-cvent-id': data_id})
            return elem.get_text(strip=True) if elem else ""
        except:
            return ""

    def safe_extract_image(self, card):
        """Safely extract image URL from card"""
        try:
            img_elem = card.find('img', {'data-cvent-id': 'speaker-card-user-profile-image'})
            return img_elem.get('src') if img_elem and img_elem.get('src') else ""
        except:
            return ""

    def find_associated_session(self, speaker_card, soup):
        """Find session information for a speaker"""
        try:
            session_container = speaker_card.find_parent('div', {'data-cvent-id': 'agenda-v2-widget-session-tile-card'})
            
            if session_container:
                return {
                    'session_title': self.safe_extract_session_text(session_container, 'session-tile-card-session-name'),
                    'speaking_time': self.safe_extract_session_text(session_container, 'session-tile-card-session-time'),
                    'location': self.safe_extract_session_text(session_container, 'session-list-card-session-location'),
                    'session_description': self.safe_extract_session_text(session_container, 'session-tile-card-session-description', max_length=500)
                }
        except:
            pass
        return None

    def safe_extract_session_text(self, container, data_id, max_length=None):
        """Safely extract session text"""
        try:
            elem = container.find('div', {'data-cvent-id': data_id})
            if elem:
                text = elem.get_text(strip=True)
                if max_length and len(text) > max_length:
                    text = text[:max_length] + "..."
                return text
        except:
            pass
        return ""

    async def extract_speakers_from_sessions(self, soup):
        """Extract additional speakers from session content"""
        logger.info("🔍 Looking for additional speakers in session content...")
        
        sessions = soup.find_all('div', {'data-cvent-id': 'agenda-v2-widget-session-tile-card'})
        
        for session in sessions:
            try:
                session_title = self.safe_extract_session_text(session, 'session-tile-card-session-name')
                session_time = self.safe_extract_session_text(session, 'session-tile-card-session-time')
                location = self.safe_extract_session_text(session, 'session-list-card-session-location')
                description = self.safe_extract_session_text(session, 'session-tile-card-session-description')
                
                full_text = f"{session_title} {description}"
                
                # Look for speaker patterns
                patterns = [
                    r'((?:Mr\.|Ms\.|Dr\.|General|Admiral|Colonel|Lieutenant|The Honorable|Mayor|Command Sergeant Major)\s+[A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
                    r'(Jeff\s+Pottinger|Matt\s+Stevens)',
                ]
                
                for pattern in patterns:
                    matches = re.finditer(pattern, full_text, re.IGNORECASE)
                    for match in matches:
                        name = match.group(1).strip()
                        
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
                            'image_url': '',
                            'detailed_bio': ''
                        }
                        
                        self.speakers_data.append(speaker_info)
                        logger.info(f"  ✅ Found additional speaker: {name}")
                        
            except Exception as e:
                continue

    def remove_duplicates(self):
        """Remove duplicate speakers"""
        unique_speakers = []
        seen_names = set()
        
        for speaker in self.speakers_data:
            name_key = re.sub(r'[^\w\s]', '', speaker['name'].lower()).strip()
            if name_key not in seen_names:
                seen_names.add(name_key)
                unique_speakers.append(speaker)
        
        self.speakers_data = unique_speakers
        logger.info(f"🔄 After deduplication: {len(self.speakers_data)} unique speakers")

    def save_to_json(self, filename="sof_week_speakers_complete.json"):
        """Save speakers data to JSON file"""
        try:
            output_data = {
                'scraped_at': datetime.now().isoformat(),
                'total_speakers': len(self.speakers_data),
                'speakers_with_detailed_bios': self.successful_bios,
                'processed_speakers': self.processed_speakers,
                'source_url': self.base_url,
                'cvent_url': self.cvent_url,
                'description': 'SOF Week 2025 Complete Speaker List with FIXED Bio Extraction',
                'speakers': self.speakers_data
            }
            
            # Save to parent directory
            scraper_file = os.path.join('..', filename)
            
            with open(scraper_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Saved {len(self.speakers_data)} speakers to {scraper_file}")
            
        except Exception as e:
            logger.error(f"❌ Error saving to JSON: {e}")

async def main():
    scraper = FixedBackgroundSOFScraper()
    
    try:
        speakers = await scraper.scrape_speakers()
        
        logger.info(f"\n🎯 FIXED SCRAPING COMPLETE!")
        logger.info(f"📊 Total speakers found: {len(speakers)}")
        logger.info(f"📝 Speakers with detailed bios: {scraper.successful_bios}")
        
        scraper.save_to_json()
        
        # Print summary of speakers with bios
        bio_speakers = [s for s in speakers if s.get('detailed_bio') and len(s['detailed_bio']) > 50]
        if bio_speakers:
            logger.info(f"\n👥 SPEAKERS WITH DETAILED BIOS:")
            for i, speaker in enumerate(bio_speakers, 1):
                logger.info(f"{i}. {speaker['name']} ({speaker.get('title', 'N/A')})")
        
        return speakers
        
    except KeyboardInterrupt:
        logger.info("🛑 Scraping interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
