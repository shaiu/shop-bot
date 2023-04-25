"""Bot commands for the Ramy Levy telegram bot"""
import logging
import os

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram.parsemode import ParseMode

WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
PORT = int(os.environ.get('PORT', 5001))
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

SHOP_URL = "http://shop:5001"

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def show_cart(update, context):
    """
    show cart command to show the current list in memory
    :param update: telegram api update
    :param context: telegram api context
    """
    logger.info("showing cart")
    response = requests.get(f"{SHOP_URL}/cart")
    text = ""
    for item in response.json():
        text += f"{item['id']}. {item['name']}\n"
    if text == "":
        logger.info("no items in cart")
        update.message.reply_text("no items in cart")
        return
    logger.info("items in cart: %s", text)
    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


def add_item(update, context):
    """
    add item to cart
    :param update: telegram api update
    :param context: telegram api context
    """
    item = update.message.text
    logger.info("got text from user <%s>", item)
    response = requests.get(f"{SHOP_URL}/catalog/{item}")
    items = response.json()
    context.bot_data['items'] = items
    kblist = list(map(lambda cart_item:
                      [InlineKeyboardButton(cart_item['name'], callback_data=cart_item['id'])],
                      items))
    reply_markup = InlineKeyboardMarkup(kblist)

    update.message.reply_text("Please choose:", reply_markup=reply_markup)


def button(update: Update, context) -> None:
    """
    add the chosen item to memory
    :param update: telegram api update
    :param context: telegram api context
    """
    query = update.callback_query
    query.answer()
    item_id = query.data
    items = context.bot_data['items']
    filtered_item = list(filter(lambda item: str(item['id']) == item_id, items))[0]
    logger.info("adding item <%s> to cart", filtered_item['name'])
    response = requests.post(f"{SHOP_URL}/cart", json=filtered_item)
    logger.info(f"status code from adding cart {response.status_code}")
    query.delete_message()


def shop(update: Update, context) -> None:
    logger.info("shopping")
    response = requests.post(f"{SHOP_URL}/shop")
    logger.info(f"status code from shopping {response.status_code}")
    update.message.reply_text("https://www.rami-levy.co.il/he", parse_mode=ParseMode.MARKDOWN)


def clear(update, context) -> None:
    logger.info("clear cart")
    response = requests.delete(f"{SHOP_URL}/cart")
    logger.info(f"status code from clear {response.status_code}")
    update.message.reply_text("cart cleared", parse_mode=ParseMode.MARKDOWN)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("cart", show_cart))
    dispatcher.add_handler(CommandHandler("shop", shop))
    dispatcher.add_handler(CommandHandler("clear", clear))
    dispatcher.add_handler(MessageHandler(Filters.text, add_item))
    dispatcher.add_handler(CallbackQueryHandler(button))

    # log all errors
    dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN,
                          webhook_url=f'{WEBHOOK_URL}/{TOKEN}')

    updater.idle()


if __name__ == '__main__':
    main()
