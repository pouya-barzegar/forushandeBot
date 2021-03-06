import logging
import os
import subprocess

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import apifetch
import dbase

# adding a logger to monitor crashes and easier debugging
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(filename='./telegbot.log',
                    format=LOG_FORMAT,
                    filemode='w',
                    level=logging.DEBUG)

logger = logging.getLogger()

global baseurl_g
baseurl_g = "http://ka2yab.com:8000/api/"


def get_token():
    token = os.getenv("FORUSHANDE_BOT")
    if token is None or not token:
        token = subprocess.call(["echo", "$FORUSHANDE_BOT"])

    if token:
        print(token)
        return token
    # raise Exception("Err: shell variable not fonud")


def start(bot, update):

    update.message.reply_text('خوش آمدید!')
    logger.info("start command used by {} "
                .format(update.message.from_user.first_name))
    logger.debug("new user << {} >>started the bot"
                 .format(update.message.from_user))

    reply_markup = parents_menu(bot, update)
    logger.debug("a keyboard was generated from categories")

    update.message.reply_text('Please choose a category:',
                              reply_markup=reply_markup)
    logger.info("message with keyboard was sent")


def help(bot, update):
    update.message.reply_text(
        'Help\n'
        'dear ` {} `,\n'
        'here are the commands for this bot:\n'
        '/start - starts the bot\n'
        '/help - shows this message\n'
        '/hell - go to hell\n'.format(update.message.from_user.first_name))
    logger.debug("help message is set")
    logger.info("help command used by {}"
                .format(update.message.from_user.first_name))


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    """
    :param buttons: a list of buttons.
    :param n_cols:  how many columns to show the butt,ons in
    :param header_buttons:  list of buttons appended to the beginning
    :param footer_buttons:  list of buttons added to the end
    :return: the menu
    """
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    print(buttons)
    logger.debug("buttons created")
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    logger.debug("header and footer buttons added")
    print(InlineKeyboardButton(menu))
    return InlineKeyboardMarkup(menu)


def button_parent(bot, update):
    query = update.callback_query
    logger.debug("a query was sent to parents Qhandler {}".format(query.data))

    baseurl = baseurl_g
    suburl = "category/subs/all/{}".format(query.data[5:])
    child_categories = apifetch.fetch_json(baseurl, suburl)
    cat_names, cat_menu = gen_category(child_categories, "name", "id", "caid:")
    reply_markup = build_menu(cat_menu, n_cols=3)
    logger.debug("query handler parent built a menu")

    bot.send_message(text="Selected: %s" % query.data[5:],
                     chat_id=query.message.chat_id,
                     reply_markup=reply_markup,
                     parse_mode='HTML')
    query.answer()
    logger.debug("callback query handled by button_parent")


def button_category(bot, update):
    query = update.callback_query
    logger.debug("a query was sent for category qhandler {}".format(query.data))
    baseurl = baseurl_g
    suburl = "category/products/{}".format(query.data[5:])
    products = apifetch.fetch_json(baseurl, suburl)
    product_names, product_menu = gen_category(products, "name", "id", "prid:",
                                               url="http://www.ka2yab.com/products/{}")

    baseurl = baseurl_g
    suburl = "category/subs/all/{}".format(query.data[5:])
    sub_cats = apifetch.fetch_json(baseurl, suburl)
    cat_names, cats_menu = gen_category(sub_cats, "name", "id", "caid:")

    reply_markup = build_menu(product_menu, n_cols=1, header_buttons=cats_menu)
    bot.send_message(text="there are Sub categories and products here:",
                     chat_id=query.message.chat_id,
                     reply_markup=reply_markup,
                     parse_mode='HTML')
    query.answer()
    logger.debug("callback query handled by button_parent")


def button_more(bot, update):
    query = update.callback_query
    data_base = dbase.start_redis(db=2)
    more_buttons = data_base.get("more_buttons")
    query.edit_message_reply_markup(reply_markup=more_buttons)
    logger.debug("callback query handled by button_more")


def parents_menu(bot, update):
    categories = apifetch.fetch_json(baseurl_g,
                                     "category/parents")
    # TODO: implement fetch from database instead of url
    logger.debug("update categories requested!")

    option_btn = 'name'
    callback = 'id'

    parent_names, button_list = gen_category(categories, option_btn,
                                             callback, "paid:")
    if len(parent_names) < 6:
        reply_markup = build_menu(button_list, n_cols=3)
    else:
        show_more = InlineKeyboardButton("بیشتر...",
                                         callback_data="more_categories")
        button_rest = button_list[6:]
        del button_list[6:]
        reply_markup = build_menu(button_list, n_cols=3,
                                  footer_buttons=[show_more])
    logger.debug("reply keyboard for category was returned")

    return reply_markup


def gen_category(categories, buttonfield,
                 callbackfield, callbackheader, url=""):
    cat_names = []
    for item in categories:
        print(item)
        cat_names.append(item[buttonfield])
    logger.info("generated a list from the name of categories; {}"
                .format(cat_names))

    button_list = [InlineKeyboardButton(s, url=url.format(str(categories[cat_names.index(s)][callbackfield])),
                                        callback_data=callbackheader + str(categories[cat_names.index(s)][callbackfield]))
                   for s in cat_names]
    return cat_names, button_list
