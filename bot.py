import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from datetime import datetime
import pytz

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot states
NAME, SURNAME, EMAIL = range(3)

# Your token list
TOKENS = [
    "J7#kL9@mN2!pQ", "xY5$fT8&zR1*wP", "qW3^bV6%nM4#sX", "8K@dH5!jL9$rF2",
    "pE7&mU3*zT6#qY", "aB4$cN8!kO2%jI", "9X#gZ5@hP1&lK3", "rS6^vD2*wF7%mQ",
    "3L@kY9!tR5$jH8", "bN7%mW4#qV1&pX", "5T#fK8@jH2!lP6", "wQ3$dM7%nB4^vZ",
    # ... (include all your tokens here)
]

# Database file
DB_FILE = "user_data.db"
TOKEN_FILE = "used_tokens.db"

def init_db():
    """Initialize database files if they don't exist"""
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            f.write("chat_id,name,surname,email,token,date\n")
    if not os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "w") as f:
            f.write("token,used\n")
            # Mark all tokens as unused initially
            for token in TOKENS:
                f.write(f"{token},0\n")

def get_available_token():
    """Get the first available token from the list"""
    with open(TOKEN_FILE, "r+") as f:
        lines = f.readlines()
        for i, line in enumerate(lines[1:], 1):  # Skip header
            token, used = line.strip().split(",")
            if used == "0":
                # Mark token as used
                lines[i] = f"{token},1\n"
                f.seek(0)
                f.writelines(lines)
                f.truncate()
                return token
    return None

def save_user_data(chat_id, name, surname, email, token):
    """Save user data to the database"""
    date = datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
    with open(DB_FILE, "a") as f:
        f.write(f"{chat_id},{name},{surname},{email},{token},{date}\n")

def start(update: Update, context: CallbackContext) -> int:
    """Start the conversation and ask for name"""
    update.message.reply_text(
        "Welcome to our Airdrop Bot! 🎉\n\n"
        "To participate, please provide the following details:\n\n"
        "What is your first name?"
    )
    return NAME

def name(update: Update, context: CallbackContext) -> int:
    """Store the name and ask for surname"""
    context.user_data['name'] = update.message.text
    update.message.reply_text("Great! What is your surname?")
    return SURNAME

def surname(update: Update, context: CallbackContext) -> int:
    """Store the surname and ask for email"""
    context.user_data['surname'] = update.message.text
    update.message.reply_text("Almost done! What is your email address?")
    return EMAIL

def email(update: Update, context: CallbackContext) -> int:
    """Store the email, provide token, and end conversation"""
    email = update.message.text
    context.user_data['email'] = email
    
    # Get an available token
    token = get_available_token()
    
    if token:
        # Save user data
        save_user_data(
            update.message.chat_id,
            context.user_data['name'],
            context.user_data['surname'],
            email,
            token
        )
        
        update.message.reply_text(
            f"🎉 Congratulations! 🎉\n\n"
            f"Here is your unique token:\n\n"
            f"<code>{token}</code>\n\n"
            f"Make sure to save it securely!\n\n"
            f"Thank you for participating in our airdrop!",
            parse_mode="HTML"
        )
    else:
        update.message.reply_text(
            "😢 All tokens have been distributed for this month.\n\n"
            "Please check back next month for new opportunities!"
        )
    
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancel the conversation"""
    update.message.reply_text(
        "Airdrop registration cancelled. "
        "Type /start if you want to try again."
    )
    return ConversationHandler.END

def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot"""
    # Initialize databases
    init_db()
    
    # Create the Updater and pass it your bot's token
    updater = Updater(os.getenv("TELEGRAM_TOKEN"))
    
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    
    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, name)],
            SURNAME: [MessageHandler(Filters.text & ~Filters.command, surname)],
            EMAIL: [MessageHandler(Filters.text & ~Filters.command, email)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    dp.add_handler(conv_handler)
    
    # Log all errors
    dp.add_error_handler(error)
    
    # Start the Bot
    updater.start_polling()
    
    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
