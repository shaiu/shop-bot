"""Bot commands for the Ramy Levy telegram bot"""
import logging
import os

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
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
    item_number = 1
    for item in response.json():
        text += f"{item_number}. {item['name']}\n"
        item_number += 1
    if text == "":
        logger.info("no items in cart")
        update.message.reply_text("no items in cart")
        return
    logger.info("items in cart: %s", text)
    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


def item_search(update, context):
    """
    command to search for an item in the catalog and return the categories
    :param update: telegram api update
    :param context: telegram api context
    """
    item = update.message.text
    logger.info("got text from user <%s>", item)
    response = requests.get(f"{SHOP_URL}/catalog/{item}")
    items = response.json()
    context.bot_data['items'] = items
    kblist = list(
        map(lambda x: [InlineKeyboardButton(x, callback_data=x)], list(set(map(lambda x: x['department'], items)))))
    reply_markup = InlineKeyboardMarkup(kblist)

    update.message.reply_text("Please choose:", reply_markup=reply_markup)

    return 'CHOOSE_CATEGORY'


def category_button(update: Update, context):
    """
    show the items in the chosen category
    :param update: telegram api update
    :param context: telegram api context
    """
    query = update.callback_query
    query.answer()
    department = query.data
    items = context.bot_data['items']
    filtered_items = list(filter(lambda item: str(item['department']) == department, items))

    kblist = list(
        map(lambda cart_item: [
            InlineKeyboardButton('%s - %s₪' % (cart_item['name'], cart_item["price"]), callback_data=cart_item['id'])],
            filtered_items))
    reply_markup = InlineKeyboardMarkup(kblist)

    query.message.reply_text("Please choose:", reply_markup=reply_markup)

    query.delete_message()

    return 'CHOOSE_ITEM'


def item_button(update: Update, context):
    """
    add the chosen item to the cart
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


# Cancel handler
def cancel(update, context):
    update.message.reply_text("Search canceled.", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


# Cancel handler
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text & ~Filters.command, item_search)],
        states={
            'CHOOSE_CATEGORY': [CallbackQueryHandler(category_button)],
            'CHOOSE_ITEM': [CallbackQueryHandler(item_button)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    dispatcher.add_handler(CommandHandler("cart", show_cart))
    dispatcher.add_handler(CommandHandler("shop", shop))
    dispatcher.add_handler(CommandHandler("clear", clear))

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
