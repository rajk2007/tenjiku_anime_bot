import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
MONGO_URI = os.environ.get("MONGO_URI")
ADMIN_IDS = [int(i) for i in os.environ.get("ADMIN_IDS", "").split(",") if i]

REQUIRED_JOIN = "Crunchyroll_offical_hindi"     # your public channel username (without @)
CHANNEL_ID = -1002570135520                     # your private channel ID

DB_NAME = "tenjiku_db"
COLLECTION_NAME = "anime"
