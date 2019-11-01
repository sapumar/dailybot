# Variables set on environment

# Required
TOKEN = os.environ["TOKEN"]
NAME = os.environ["NAME"]
HOUR = int(os.environ["HOUR"])
MINUTE = int(os.environ["MINUTE"])
DAILY_TIME = datetime.time(hour=HOUR, minute=MINUTE)

chat_ids = os.environ["CHAT_ID"].replace(" ", "").split(",")

# Port is given by Heroku/ngrok
PORT = os.environ.get("PORT", None)
LINK = os.environ.get("LINK", None)