import logging
from constants import *
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import io
import os

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    message_text = update.message.text
    
    if message_text.lower() == PASSWORD:
        try:
            # Fetch data from Redis using the lock name
            data = redis_client.get(REDIS_LOCK_NAME)
            if data:
                # Parse Redis data
                redis_data = data.decode("utf-8").split('\n')
                flag = redis_data[0].strip().lower()  # Extract flag (first line)
                image_url = redis_data[1].strip()     # Extract image URL (second line)
                text_data = "\n".join(redis_data[2:]).strip()  # Extract text data
                
                if flag == "true":
                    # Send photo message with the retrieved image URL and text data
                    await context.bot.send_photo(update.message.chat_id, photo=image_url, caption=text_data)
                elif flag == "false":
                    # If flag is false, fall back to using local image
                    local_image_path = IMAGE_PATH
                    with open(local_image_path, "rb") as img_file:
                        await context.bot.send_photo(update.message.chat_id, photo=img_file, caption=text_data)
                else:
                    await update.message.reply_text("Invalid flag value in Redis data.")
            else:
                await update.message.reply_text("No data found for the specified lock.")
        except Exception as e:
            await update.message.reply_text(f"Error fetching data from Redis: {e}")
    else:
        # If the message is not the password, forward it to your personal Telegram account
        try:
            # Replace 'MAIN_ACCOUNT_USER_ID' with your main account's Telegram user ID
            # Retrieve the sender's username
            user = update.effective_user
            
            # Combine sender's username and message text
            sender_info = f"From: {user.full_name}\n\n"
            forwarded_message = sender_info + message_text
            
            # Forward the combined message to your main account
            await context.bot.send_message(chat_id=MAIN_ACCOUNT_USER_ID, text=forwarded_message)
        except Exception as e:
            # If forwarding fails, log the error and proceed silently
            logger.error(f"Error forwarding message: {e}")
        
        user = update.effective_user
        response = user.full_name + ", " + REPLAY_MESSAGE
        
    await update.message.reply_text(response)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()
    
    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()