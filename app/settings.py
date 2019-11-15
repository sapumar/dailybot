import os
import datetime


# Variables set on environment when possible

# Required
TOKEN = os.environ.get("TOKEN", "")
NAME = os.environ.get("NAME", "")
HOUR = int(os.environ.get("HOUR", 10))
MINUTE = int(os.environ.get("MINUTE", 00))
DAILY_TIME = datetime.time(hour=HOUR, minute=MINUTE)

chat_ids = os.environ.get("CHAT_ID", "").replace(" ", "").split(",")

# Port and link is given by Heroku/ngrok
PORT = os.environ.get("PORT", None)
LINK = os.environ.get("LINK", None)