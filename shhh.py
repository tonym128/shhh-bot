import logging
import logging.handlers
#import pprint
from telegram import Update #, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import os
#import shlex
from subprocess import Popen, PIPE
import time
import dbm
import uuid
import re

_to_esc = re.compile(r'\s|[]()[]')
def _esc_char(match):
    return '\\' + match.group(0)
 
def my_escape(name):
    return _to_esc.sub(_esc_char, name)

API_KEY = os.getenv('SHHH_API_KEY')
MY_CHAT_ID = os.getenv('SHHH_MY_CHAT_ID')
logFormat = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(
    format=logFormat,
    level=logging.INFO,
    filename="log.txt"
)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logging.Formatter(logFormat))
logging.getLogger().addHandler(consoleHandler)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = "Hi, I'm a bot who wants to help you keep quiet, let me take your voice notes and speech to text them!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=txt)
    await context.bot.send_message(chat_id=MY_CHAT_ID, text=txt)
    logging.info("start - effective chat id: %s - txt: %s", update.effective_chat.id, txt)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = "Sorry, I didn't understand that command."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=txt)
    await context.bot.send_message(chat_id=MY_CHAT_ID, text=txt)
    logging.info("unknown - effective chat id: %s - txt: %s", update.effective_chat.id, txt)

async def handle_message(update, context):
    username = str(update.message.chat.username)
    chat_id = update.message.chat_id
    start = time.time()
    fileid = uuid.uuid4().hex
    logging.info("Started processing for "+username)
    await context.bot.send_message(chat_id=MY_CHAT_ID, text="Started processing for "+username)
    try:
        file = await context.bot.get_file(update.message.effective_attachment.file_id)

        # File Size Check 50mb
        if file.file_size > 50*1024*1024:
            end = time.time()
            logging.log(logging.INFO,str(end-start) + " " + username + " : " + str(chat_id) + ": FAIL SIZE : " + str(file.file_size) + "Message was too big for processing, there is a 50mb limit")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Message was too big for processing, there is a 50mb limit")
            await context.bot.send_message(chat_id=MY_CHAT_ID, text="Message was too big for processing, there is a 50mb limit")
            return

        # Duration Check 650s
        try:
            if update.message.effective_attachment.duration > 650:
                end = time.time()
                logging.log(logging.INFO,str(end-start) + " " + username + " : " + str(chat_id)  + " : FAIL TIME : " + str(update.message.effective_attachment.duration) + " Cannot process audio longer than 60 seconds")
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Cannot process audio longer than 600 seconds")
                await context.bot.send_message(chat_id=MY_CHAT_ID, text="Cannot process audio longer than 600 seconds")
                return
        except:
            end = time.time()
            logging.log(logging.INFO,str(end-start) + " " + username + " : " + str(chat_id)  + " : FAIL NOTIME : Does not look like a type I can process, exiting")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Does not look like a type I can process, exiting")
            await context.bot.send_message(chat_id=MY_CHAT_ID, text="Does not look like a type I can process, exiting")
            return

        # Download and process
        source_file = await file.download_to_drive(custom_path="/tmp/"+fileid)
        filename = str(source_file)
        cmd = 'sh ./convert.sh '+my_escape(filename) + " >> convert.log"
        process = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
        process.wait()

        result = open(filename+".wav.txt", "r")
        text = result.read()
        result.close()
        os.remove(filename)
        os.remove(filename+".wav")
        os.remove(filename+".wav.txt")
        logging.log(logging.INFO,text)
        end = time.time()
        logline = str(end-start) + " " + username + " : " + str(chat_id)  + " : SUCCESS : " + str(update.message.effective_attachment.duration)
        logging.log(logging.INFO,logline)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

        db = dbm.open('data_store', 'c')
        value = 1
        if db.get(username):
            value = int(db[username])+1
        db[str(username)] = str(value)
        db.close()

        await context.bot.send_message(chat_id=MY_CHAT_ID, text=logline)
    except:
        end = time.time()
        logging.log(logging.ERROR,str(end-start) + " " + username + " : " + str(chat_id)  + " : FAIL UNKNOWN : Failed processing message")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Failure processing your message")
        await context.bot.send_message(chat_id=MY_CHAT_ID, text="Failure processing your message")


if __name__ == '__main__':
    exitt = False
    if API_KEY == None:
        logging.info("SHHH_API_KEY must be defined")
        exitt = True
    if MY_CHAT_ID == None:
        logging.info("SHHH_MY_CHAT_ID must be defined")
        exitt = True

    if not exitt:
        application = ApplicationBuilder().token(API_KEY).build()
        logging.info("Starting bot")
        start_handler = CommandHandler('start', start)
        application.add_handler(start_handler)
        unknown_handler = MessageHandler(filters.COMMAND, unknown)
        application.add_handler(unknown_handler)

        application.add_handler(MessageHandler(filters.ATTACHMENT, handle_message))
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        logging.info("Bot await messages")
    else:
        logging.info("Failed to run, please resolve exports issue and run again")