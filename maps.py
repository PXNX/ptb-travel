import regex as re
import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CallbackContext, MessageHandler, filters
from constant import MAPS_URL
from urllib.parse import unquote

# The Google Maps short link
async def scrap_map(update: Update, context: CallbackContext):
    urls = re.finditer(MAPS_URL, update.message.text)
    for url_match in urls:
        url = url_match.group(0)
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.google.com/',
            }
            
            session = requests.Session()
            session.headers.update(headers)
            
            logging.info(f"Fetching Google Maps URL: {url}")
            response = session.get(url, allow_redirects=True, timeout=15)
            final_url = response.url
            
            if response.status_code != 200:
                logging.error(f"Failed to fetch page '{final_url}'. Status code: {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to extract name from OG tags
            og_title = soup.find('meta', property='og:title')
            name_extract = og_title['content'] if og_title and og_title.get('content') else 'Google Maps'
            
            # Try to extract image from OG tags
            og_image = soup.find('meta', property='og:image')
            image_url = og_image['content'] if og_image and og_image.get('content') else None
            
            logging.info(f"Initial extraction - Name: {name_extract}, Image: {image_url}")

            # Refine name if it's generic "Google Maps"
            title = name_extract
            location = "Google Maps"
            
            if name_extract == "Google Maps" or " · " not in name_extract:
                # Try to extract from URL
                if "/maps/place/" in final_url:
                    place_part = final_url.split("/maps/place/")[1].split("/")[0]
                    title = unquote(place_part).replace("+", " ")
                    location = "Google Maps"
                elif " · " in name_extract:
                    parts = name_extract.split(' · ')
                    title = parts[0]
                    location = parts[1]
            else:
                parts = name_extract.split(' · ')
                title = parts[0]
                location = parts[1]

            caption = f"<b>{title}</b>\n\n📌 #{location.replace(' ', '_')}\n\n🔗 {url}"
            
            if image_url:
                await update.message.reply_photo(photo=image_url, caption=caption)
            else:
                await update.message.reply_text(text=caption)
                
        except Exception as e:
            logging.error(f"Error in scrap_map: {e}")

def register_maps(app: Application):
    app.add_handler(MessageHandler(filters.Regex(MAPS_URL), scrap_map))
