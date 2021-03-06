import logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import telegbot

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(filename='./telegbot.log',
                             format=LOG_FORMAT,
                             filemode='w',
                             level=logging.INFO)

logger = logging.getLogger()

token = telegbot.get_token()
updates = Updater(token)

logger.info("adding dispatchers")


updates.dispatcher.add_handler(CommandHandler('start', telegbot.start))
updates.dispatcher.add_handler(CommandHandler('help', telegbot.help))

updates.dispatcher.add_handler(CallbackQueryHandler(telegbot.button_parent,
                                                    pattern="paid.*"))
updates.dispatcher.add_handler(CallbackQueryHandler(telegbot.button_category,
                                                    pattern="caid.*"))
updates.dispatcher.add_handler(CallbackQueryHandler(telegbot.button_more,
                                                    pattern="more.*"))

logger.info("all commands configured")


updates.start_polling()
updates.idle()
