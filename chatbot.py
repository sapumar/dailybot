import logging
import datetime
import os
import sys
from configparser import ConfigParser
from time import sleep

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


class Chatbot:

    def __init__(self, token):
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=logging.INFO,
        )
        self.logger = logging.getLogger("LOG")
        self.logger.info("Starting bot.")
        self.updater = Updater(token)
        self.dispatcher = self.updater.dispatcher

        self.job = self.updater.job_queue

        daily_hour = int(os.environ.get("HOUR"))
        daily_minute = int(os.environ.get("MINUTE"))
        daily_time = datetime.time(hour=daily_hour, minute=daily_minute)
        self.job_daily = self.job.run_daily(self.send_daily, time=daily_time)

        start_handler = CommandHandler("start", self.send_start)
        self.dispatcher.add_handler(start_handler)

        example_handler = CommandHandler("exemplo", self.send_example)
        self.dispatcher.add_handler(example_handler)

        self.dispatcher.add_error_handler(self.error)

    @staticmethod
    def send_type_action(chatbot, update):
        """
        Shows status typing when sending message
        """
        chatbot.send_chat_action(
            chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING
        )
        sleep(1)

    def send_start(self, chatbot, update):
        """
        Start command to receive /start message on Telegram.
        @bot = information about the bot
        @update = the user info.
        """
        self.logger.info("Start command received.")
        self.logger.info(f"{update}")
        self.send_type_action(chatbot, update)
        name = update.message["chat"]["first_name"]
        start_text = (
            f"Olá, estou aqui para te lembrar de mandar sua daily todo dia! TODO. SANTO. DIA."
        )
        chatbot.send_message(
            chat_id=update.message.chat_id,
            text=start_text,
            parse_mode=telegram.ParseMode.MARKDOWN,
        )
        return 0

    def send_daily(self, chatbot, job):
        """
        Info command to know more about the developers.
        @bot = information about the bot
        @update = the user info.
        """
        chat_id = os.environ.get("CHAT_ID")
        self.logger.info(f"Sending daily to {chat_id}")
        with open("daily.md") \
                as daily_file:
            daily_text = daily_file.read()
            chatbot.send_message(
                chat_id=chat_id,
                text=daily_text,
                parse_mode=telegram.ParseMode.MARKDOWN,
            )
            return 0

    def send_example(self, chatbot, update):
        """
        Sends example to caller
        @chatbot = information about the bot
        @update = the user info.
        """
        self.send_type_action(chatbot, update)
        self.logger.info("Example command received.")
        with open("exemplo.md") \
                as example_file:
            example_text = example_file.read()
            print(example_text)
            chatbot.send_message(
                chat_id=update.message.chat_id,
                text=example_text,
                parse_mode=telegram.ParseMode.MARKDOWN,
            )
            return 0

    def text_message(self, chatbot, update):
        self.send_type_action(chatbot, update)

        chatbot.send_message(
            chat_id=update.message.chat_id,
            text="ok",
            parse_mode=telegram.ParseMode.MARKDOWN,
        )
        return 0

    def error(self, chatbot, update, error):
        self.logger.warning(f'Update "{update}" caused error "{error}"')
        return 0

    def run(self):
        # Start the Bot
        self.logger.info("Polling bot.")
        self.updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        self.updater.idle()
        return 0


if __name__ == "__main__":
    # Variables set on Heroku
    TOKEN = os.environ.get("TOKEN")
    NAME = os.environ.get("NAME")
    # Port is given by Heroku
    PORT = os.environ.get("PORT")
    if TOKEN is not None:
        if PORT is not None:
            bot = Chatbot(TOKEN)
            bot.updater.start_webhook(
                listen="0.0.0.0",
                port=int(PORT),
                url_path=TOKEN)
            bot.updater.bot.set_webhook(f"https://{NAME}.herokuapp.com/{TOKEN}")
            bot.updater.idle()
        else:
            # Run on local system once detected that it's not on Heroku
            bot = Chatbot(TOKEN)
            bot.run()
