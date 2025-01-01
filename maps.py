import regex as re
import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CallbackContext, MessageHandler, filters

from constant import MAPS_URL


# The Google Maps short link

async def scrap_map(update: Update, context: CallbackContext):
    urls = re.finditer(MAPS_URL,  update.message.text)

    for url in urls:

        try:
            response = requests.get(url.string, allow_redirects=True)
            final_url = response.url

            response = requests.get(url.string)
            if response.status_code != 200: # seems to run into 429
                logging.error(f"Failed to fetch page '{final_url}'. Status code: {response.status_code}")
                return

            soup = BeautifulSoup(response.text, 'html.parser')

            name = soup.find('meta', property='og:title')
            name_extract = name['content'] if name else 'Name not found'

            image_meta = soup.find('meta', property='og:image')
            image_url = image_meta['content'] if image_meta else 'Image not found'

            logging.info(f"Name: {name_extract} - Image URL: {image_url}")

            title = name_extract.split(' · ')[0]
            location = name_extract.split(' · ')[1]

            caption = f"<b>{title}</b>\n\n📌 #{location}\n\n🔗 {url}"

            await update.message.reply_photo(photo=image_url, caption=caption)

        except Exception as e:
            logging.error(f"Error in scrap_map: {e}")


def register_maps(app: Application):
    app.add_handler(MessageHandler(filters.Regex(MAPS_URL), scrap_map))