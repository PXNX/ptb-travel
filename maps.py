import re

import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CallbackContext, MessageHandler, filters

from constant import MAPS_URL


# The Google Maps short link

async def scrap_map(update:Update,context: CallbackContext):
    url = update.message.text

    # Follow the redirect to get the final URL
    response = requests.get(url, allow_redirects=True)
    final_url = response.url  # Get the redirected URL

    # Fetch the HTML content of the final URL
    response = requests.get(final_url)
    if response.status_code != 200:
        print(f"Failed to fetch page. Status code: {response.status_code}")
        exit()

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract the name (title of the page)
    name = soup.find('meta', property='og:title')
    name_extract = name['content'] if name else 'Name not found'

    # Extract the image URL from meta tags
    image_meta = soup.find('meta', property='og:image')
    image_url = image_meta['content'] if image_meta else 'Image not found'

    print(f"Name: {name_extract}")
    print(f"Image URL: {image_url}")

    title = name_extract.split(' · ')[0]
    location = name_extract.split(' · ')[1]


    caption = f"<b>{title}</b>\n\n📌 #{location}\n\n🔗 {url}"

    await update.message.reply_photo(photo=image_url, caption=caption)



def register_maps(app: Application):
    app.add_handler(MessageHandler(filters.Regex(MAPS_URL), scrap_map))