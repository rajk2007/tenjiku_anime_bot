from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from pymongo import MongoClient
from config import BOT_TOKEN, MONGO_URI, DB_NAME, COLLECTION_NAME, CHANNEL_ID, REQUIRED_JOIN

import nest_asyncio
nest_asyncio.apply()

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# ✅ Check if user joined the required channel
async def check_joined(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=f"@{REQUIRED_JOIN}", user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ✅ /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_joined(update.effective_user.id, context):
        await update.message.reply_text(f"🚫 Please join our channel first: https://t.me/{REQUIRED_JOIN}")
        return

    if len(context.args) == 0:
        await update.message.reply_text("Welcome to Tenjiku Anime Hub 🌏🎌!\nUse /anime to see what's available.")
        return

    anime_id = context.args[0]
    anime = collection.find_one({"anime_id": anime_id})
    if not anime:
        await update.message.reply_text("⚠️ Anime not found!")
        return

    if "poster_msg_id" in anime:
        try:
            await context.bot.copy_message(chat_id=update.effective_chat.id, from_chat_id=CHANNEL_ID, message_id=anime["poster_msg_id"])
        except:
            await update.message.reply_text("⚠️ Failed to send poster.")

    for msg_id in anime["msg_ids"]:
        try:
            await context.bot.copy_message(chat_id=update.effective_chat.id, from_chat_id=CHANNEL_ID, message_id=msg_id)
        except:
            await update.message.reply_text(f"❌ Failed to send episode ID: {msg_id}")

# ✅ /addanime handler
async def add_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != update.effective_chat.id:
        return
    if len(context.args) < 3:
        await update.message.reply_text("Use: /addanime anime_id \"Title\" quality")
        return

    anime_id = context.args[0]
    title = context.args[1].strip("\"“”")
    quality = context.args[2]

    if collection.find_one({"anime_id": anime_id}):
        await update.message.reply_text("Anime already exists.")
        return

    collection.insert_one({
        "anime_id": anime_id,
        "title": title,
        "quality": quality,
        "msg_ids": []
    })
    await update.message.reply_text(f"✅ Added anime: {title} ({quality})")

# ✅ /addepisode handler
async def add_episode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != update.effective_chat.id:
        return
    if len(context.args) != 2:
        await update.message.reply_text("Use: /addepisode anime_id msg_id")
        return

    anime_id = context.args[0]
    msg_id = int(context.args[1])
    anime = collection.find_one({"anime_id": anime_id})

    if not anime:
        await update.message.reply_text("Anime not found.")
        return

    collection.update_one({"anime_id": anime_id}, {"$push": {"msg_ids": msg_id}})
    await update.message.reply_text(f"✅ Added episode msg_id: {msg_id} to {anime['title']}")

# ✅ /addposter handler
async def add_poster(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != update.effective_chat.id:
        return
    if len(context.args) != 2:
        await update.message.reply_text("Use: /addposter anime_id poster_msg_id")
        return

    anime_id = context.args[0]
    poster_msg_id = int(context.args[1])
    result = collection.update_one({"anime_id": anime_id}, {"$set": {"poster_msg_id": poster_msg_id}})
    if result.matched_count == 0:
        await update.message.reply_text("Anime not found.")
    else:
        await update.message.reply_text(f"✅ Poster added to {anime_id}")

# ✅ /anime list handler
async def anime_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    anime_docs = collection.find()
    if not await check_joined(update.effective_user.id, context):
        await update.message.reply_text(f"🚫 Please join our channel first: https://t.me/{REQUIRED_JOIN}")
        return

    if update.effective_user.id == update.effective_chat.id:
    pass