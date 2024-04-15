import logging
import logging.handlers
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import os
import subprocess
import time
import dbm
import uuid
import re

class ShhBot:
    API_KEY: str
    MY_CHAT_ID: str
    ALLOWED_CHAT_IDS: str
    WHISPER_MODEL: str
    WHISPER_OPTIONS: str

    logFormat = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        format=logFormat,
        level=logging.INFO,
    )

    httpx_logger = logging.getLogger("httpx")

    # Set the logging level to WARNING to ignore INFO and DEBUG logs
    httpx_logger.setLevel(logging.WARNING)

    def removefile(self, f):
    try:
        os.remove(f)
    except OSError:
        pass

    def startBot(self):
        exitt = False
        if self.API_KEY == None:
            logging.info("SHHH_API_KEY must be defined")
            exitt = True
        logging.info("SHHH_MY_CHAT_ID       : %s", self.MY_CHAT_ID)
        logging.info("SHHH_ALLOWED_CHAT_IDS : %s", self.ALLOWED_CHAT_IDS)
        logging.info("SHHH_WHISPER_MODEL    : %s", self.WHISPER_MODEL)
        logging.info("SHHH_WHISPER_OPTIONS  : %s", self.WHISPER_OPTIONS)

        if not exitt:
            if self.WHISPER_MODEL != None:
                logging.log(logging.INFO, "Download Whisper Model : " + self.WHISPER_MODEL)
                outfile = open('/tmp/download.log','w') #same with "w" or "a" as opening mode
                cmd = './download.sh'
                subprocess.Run(cmd, stdout=outfile, stderr=outfile,shell=True)
                outfile.close()
                with open("/tmp/download.log", "r") as f:
                    contents = f.read()
                logging.log(logging.INFO, contents)

            application = ApplicationBuilder().token(self.API_KEY).build()
            logging.info("Starting bot")
            start_handler = CommandHandler("start", self.start)
            application.add_handler(start_handler)
            unknown_handler = MessageHandler(filters.COMMAND, self.unknown)
            application.add_handler(unknown_handler)

            application.add_handler(MessageHandler(filters.ATTACHMENT, self.handle_message))
            application.run_polling(allowed_updates=Update.ALL_TYPES)
            logging.info("Bot await messages")
        else:
            logging.info("Failed to run, please resolve exports issue and run again")

    def _esc_char(self,match):
        return '\\' + match.group(0)

    def my_escape(self,name):
        return re.compile(r'\s|[]()[]').sub(self._esc_char, name)

    def checkUser(self, chat_id: str, allowed_chat_id_string: str):
        if allowed_chat_id_string is None:
            return True
        allow_list = allowed_chat_id_string.split(' ')
        if any(chat_id == value for value in allow_list):
            return True

        logging.info("SHHH_ALLOWED_CHAT_IDS : Not processing for %s \nAllowList %s", chat_id, allow_list)
        return False

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        txt = "Hi, I'm a bot who wants to help you keep quiet, let me take your voice notes and speech to text them!"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=txt)
        if self.MY_CHAT_ID is not None:
            await context.bot.send_message(chat_id=self.MY_CHAT_ID, text=txt)
        logging.info("start - effective chat id: %s - txt: %s", update.effective_chat.id, txt)

    async def unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        txt = "Sorry, I didn't understand that command."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=txt)
        if self.MY_CHAT_ID is not None:
            await context.bot.send_message(chat_id=self.MY_CHAT_ID, text=txt)
        logging.info("unknown - effective chat id: %s - txt: %s", update.effective_chat.id, txt)

    async def handle_message(self, update, context):
        username = str(update.message.chat.username)

        if not self.checkUser(str(update.effective_chat.id), self.ALLOWED_CHAT_IDS):
            logging.info("Not processing for %s : %s", username, update.effective_chat.id)
            if self.MY_CHAT_ID is not None:
                await context.bot.send_message(chat_id=self.MY_CHAT_ID, text="Not processing for {0} : {1}".format(username,update.effective_chat.id))
            return

        start = time.time()
        input_file = "/tmp/media"
        logging.info("Started processing for "+username)
        if self.MY_CHAT_ID is not None:
            await context.bot.send_message(chat_id=self.MY_CHAT_ID, text="Started processing for "+username)
        try:
            file = await context.bot.get_file(update.message.effective_attachment.file_id)

            # File Size Check 50mb
            if file.file_size > 50*1024*1024:
                end = time.time()
                logging.log(logging.INFO,str(end-start) + " " + username + " : " + str(update.effective_chat.id) + ": FAIL SIZE : " + str(file.file_size) + "Message was too big for processing, there is a 50mb limit")
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Message was too big for processing, there is a 50mb limit")
                if self.MY_CHAT_ID is not None:
                    await context.bot.send_message(chat_id=self.MY_CHAT_ID, text="Message was too big for processing, there is a 50mb limit")
                return

            # Duration Check 650s
            try:
                if update.message.effective_attachment.duration > 650:
                    end = time.time()
                    logging.log(logging.INFO,str(end-start) + " " + username + " : " + str(update.effective_chat.id)  + " : FAIL TIME : " + str(update.message.effective_attachment.duration) + " Cannot process audio longer than 60 seconds")
                    await context.bot.send_message(chat_id=update.effective_chat.id, text="Cannot process audio longer than 600 seconds")
                    if self.MY_CHAT_ID is not None:
                        await context.bot.send_message(chat_id=self.MY_CHAT_ID, text="Cannot process audio longer than 600 seconds")
                    return
            except:
                end = time.time()
                logging.log(logging.INFO,str(end-start) + " " + username + " : " + str(update.effective_chat.id)  + " : FAIL NOTIME : Does not look like a type I can process, exiting")
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Does not look like a type I can process, exiting")
                if self.MY_CHAT_ID is not None:
                    await context.bot.send_message(chat_id=self.MY_CHAT_ID, text="Does not look like a type I can process, exiting")
                return

            # Cleanup
            self.removefile(input_file)
            self.removefile(input_file+".wav")
            self.removefile(input_file+".wav.txt")

            # Download and process
            await file.download_to_drive(custom_path=input_file)
            logging.log(logging.INFO,"Downloaded "+ input_file)
            outfile = open('/tmp/convert.log','w') #same with "w" or "a" as opening mode
            cmd = './convert.sh'
            subprocess.Run([cmd],  stdout=outfile, stderr=outfile,shell=True)
            outfile.close()

            result = open(input_file+".wav.txt", "r")
            text = result.read()
            result.close()
            self.removefile(input_file)
            self.removefile(input_file+".wav")
            self.removefile(input_file+".wav.txt")
            logging.log(logging.INFO,text)
            end = time.time()
            logline = str(end-start) + " " + username + " : " + str(update.effective_chat.id)  + " : SUCCESS : " + str(update.message.effective_attachment.duration)
            logging.log(logging.INFO,logline)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

            db = dbm.open('data_store', 'c')
            value = 1
            if db.get(username):
                value = int(db[username])+1
            db[str(username)] = str(value)
            db.close()

            if self.MY_CHAT_ID is not None:
                await context.bot.send_message(chat_id=self.MY_CHAT_ID, text=logline)
        except Exception as e :
            end = time.time()
            logging.log(logging.ERROR,str(end-start) + " " + username + " : " + str(update.effective_chat.id)  + " : FAIL UNKNOWN : Failed processing message")
            logging.log(logging.ERROR,str(e))

            await context.bot.send_message(chat_id=update.effective_chat.id, text="Failure processing your message")
            if self.MY_CHAT_ID is not None:
                await context.bot.send_message(chat_id=self.MY_CHAT_ID, text="Failure processing your message")
                await context.bot.send_message(chat_id=self.MY_CHAT_ID, text=str(e))
            try:
                with open("/tmp/convert.log", "r") as f:
                    contents = f.read()
                logging.log(logging.ERROR,contents)
                if self.MY_CHAT_ID is not None:
                    await context.bot.send_message(chat_id=self.MY_CHAT_ID, text=contents)
            except:
                logging.log(logging.ERROR,"Failed to read convert.log")
                if self.MY_CHAT_ID is not None:
                    await context.bot.send_message(chat_id=self.MY_CHAT_ID, text="Failed to read convert.log")

if __name__ == '__main__':
    shhBot = ShhBot()
    shhBot.API_KEY = os.getenv('SHHH_API_KEY')
    shhBot.MY_CHAT_ID = os.getenv('SHHH_MY_CHAT_ID')
    shhBot.ALLOWED_CHAT_IDS = os.getenv('SHHH_ALLOWED_CHAT_IDS')
    shhBot.WHISPER_MODEL = os.getenv('SHHH_WHISPER_MODEL')
    shhBot.WHISPER_OPTIONS = os.getenv('SHHH_WHISPER_OPTIONS')
    shhBot.startBot()
