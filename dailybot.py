import datetime
import logging
import os
from time import sleep

import telegram
from telegram.ext import Updater, CommandHandler


class DailyBot:

    def __init__(self, token):
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=logging.INFO,
        )
        self.logger = logging.getLogger("LOG")
        self.logger.info("Starting BOT.")
        self.updater = Updater(token)
        self.dispatcher = self.updater.dispatcher

        self.job = self.updater.job_queue

        daily_hour = int(os.environ.get("HOUR"))
        daily_minute = int(os.environ.get("MINUTE"))
        daily_time = datetime.time(hour=daily_hour, minute=daily_minute)
        self.job_daily = self.job.run_daily(self.send_daily, time=daily_time, days=(0, 1, 2, 3, 4))

        start_handler = CommandHandler("start", self.send_start)
        self.dispatcher.add_handler(start_handler)

        example_handler = CommandHandler("example", self.send_example)
        self.dispatcher.add_handler(example_handler)

        daily_handler = CommandHandler("daily", self.send_daily)
        self.dispatcher.add_handler(daily_handler)

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
        @BOT = information about the BOT
        @update = the user info.
        """
        self.logger.info("Start command received.")
        self.logger.info(f"{update}")
        self.send_type_action(chatbot, update)

        chat_id = update.message["chat"]["id"]
        if update.message["chat"]["type"] == "private":
            name = update.message["chat"]["first_name"]
        else:
            name = update.message["from_user"]["first_name"]

        with open("msg/start.md") as start_file:
            try:
                start_text = start_file.read()
                start_text = start_text.replace("{{name}}", name)
                chatbot.send_message(
                    chat_id=chat_id,
                    text=start_text,
                    parse_mode=telegram.ParseMode.MARKDOWN,
                )
            except Exception as error:
                self.logger.error(error)
        try:
            chat_ids = os.environ.get("CHAT_ID").replace(" ", "")
            chat_ids = chat_ids.split(",")
            chat_ids = [int(i) for i in chat_ids]
            if chat_id not in chat_ids:
                with open("msg/error.md") as error:
                    error = error.read()
                    chatbot.send_message(
                        chat_id=chat_id,
                        text=error,
                        parse_mode=telegram.ParseMode.MARKDOWN,
                    )
        except Exception as error:
            self.logger.error(error)
        return 0

    def send_daily(self, chatbot, job):
        """
        Sends text on `daily.md` daily to groups on CHAT_ID
        @BOT = information about the BOT
        @update = the user info.
        """
        chat_ids = os.environ.get("CHAT_ID").replace(" ", "")
        chat_ids = chat_ids.split(",")
        for chat_id in chat_ids:
            self.logger.info(f"Sending daily to {chat_id}")
            with open("msg/daily.md") as daily_file:
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
        @chatbot = information about the BOT
        @update = the user info.
        """
        self.send_type_action(chatbot, update)
        self.logger.info("Example command received.")
        with open("msg/example.md") as example_file:
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
        self.logger.info("Polling BOT.")
        self.updater.start_polling()

        # Run the BOT until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the BOT gracefully.
        self.updater.idle()
        return 0


if __name__ == "__main__":
    # Variables set on environment
    TOKEN = os.environ.get("TOKEN")
    NAME = os.environ.get("NAME")
    # Port is given by Heroku/ngrok
    PORT = os.environ.get("PORT")
    LINK = os.environ.get("LINK")
    if TOKEN is not None:
        if PORT is not None:
            BOT = DailyBot(TOKEN)
            BOT.updater.start_webhook(
                listen="0.0.0.0",
                port=int(PORT),
                url_path=TOKEN)
            if LINK:
                BOT.updater.bot.set_webhook(LINK)
            else:
                BOT.updater.bot.set_webhook(f"https://{NAME}.herokuapp.com/{TOKEN}")
            BOT.updater.idle()
        else:
            # Run on local system once detected that it's not on Heroku nor ngrok
            BOT = DailyBot(TOKEN)
            BOT.run()
    else:
        HOUR = int(os.environ.get("HOUR"))
        MINUTE = int(os.environ.get("MINUTE"))
        print(f"Token {TOKEN}\n"
              f"Port {PORT}\n"
              f"Name {NAME}\n"
              f"Hour {HOUR}\n"
              f"Minute {MINUTE}\n")
