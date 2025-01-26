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
            googleTrendsUrl = 'https://google.com'
            response = requests.get(googleTrendsUrl)
            if response.status_code == 200:
                g_cookies = response.cookies.get_dict()
            else:
                g_cookies= {}

            headers = {
                'User-agent':
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582'
            }
            response = requests.get(url.string, allow_redirects=True, headers=headers)
            final_url = response.url

            response = requests.get(url.string,headers=headers,cookies=g_cookies)
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