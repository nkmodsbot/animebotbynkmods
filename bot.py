import logging
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define environment variables
bot_token = os.environ.get('BOT_TOKEN')
admin_id = int(os.environ.get('ADMIN_ID'))

# Start command handler
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    keyboard = [[InlineKeyboardButton("Contact Admin", url="https://t.me/nkmods")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f"Hello, I'm Perfect Bot\nCreated By @nkmods", reply_markup=reply_markup)

# Request button handler
def request(update: Update, context: CallbackContext) -> None:
    """Send a message when the Request button is pressed."""
    keyboard = [[InlineKeyboardButton("Yes", callback_data='request_confirm_yes'),
                 InlineKeyboardButton("No", callback_data='request_confirm_no')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Enter your request", reply_markup=reply_markup)

# Request confirmation handler
def request_confirmation(update: Update, context: CallbackContext) -> None:
    """Process the user's request confirmation."""
    query = update.callback_query
    if query.data == 'request_confirm_yes':
        query.message.reply_text("Your request has been received.")
        # You can access the user's request using query.message.text
        # Send the request to the admin or perform any other desired action
    else:
        query.message.reply_text("Request canceled.")

# Add button handler
def add_button(update: Update, context: CallbackContext) -> None:
    """Add a new button based on the admin's input."""
    user_id = update.effective_user.id
    if user_id != admin_id:
        update.message.reply_text("You are not authorized to perform this action.")
        return

    update.message.reply_text("What do you want to put on the button name?")
    context.user_data['next_step'] = 'add_button_reply'

# Add button reply handler
def add_button_reply(update: Update, context: CallbackContext) -> None:
    """Process the admin's button name input and ask for reply options."""
    button_name = update.message.text
    update.message.reply_text("What are your reply options? (comma-separated)")
    context.user_data['button_name'] = button_name
    context.user_data['next_step'] = 'add_button_confirm'

# Add button confirm handler
def add_button_confirm(update: Update, context: CallbackContext) -> None:
    """Process the admin's reply options and add the button."""
    reply_options = update.message.text.split(',')
    button_name = context.user_data['button_name']
    user_id = update.effective_user.id

    if user_id != admin_id:
        update.message.reply_text("You are not authorized to perform this action.")
        return

    keyboard = [[InlineKeyboardButton(reply_option.strip(), callback_data=f'custom_button_{reply_option.strip()}')]
                for reply_option in reply_options]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f"Button '{button_name}' has been added.", reply_markup=reply_markup)

    context.user_data.pop('button_name')
    context.user_data.pop('next_step')

# Button callback handler
def button_callback(update: Update, context: CallbackContext) -> None:
    """Process button callbacks."""
    query = update.callback_query
    if query.data.startswith('custom_button_'):
        reply_option = query.data.replace('custom_button_', '')
        query.message.reply_text(f"You selected: {reply_option}")

# Message handler for all other messages
def message_handler(update: Update, context: CallbackContext) -> None:
    """Handle all other messages."""
    user_id = update.effective_user.id
    if user_id == admin_id and 'next_step' in context.user_data:
        next_step = context.user_data['next_step']
        if next_step == 'add_button_reply':
            add_button_reply(update, context)
        elif next_step == 'add_button_confirm':
            add_button_confirm(update, context)
        return

    update.message.reply_text("I'm sorry, I don't understand.")

def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(bot_token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("request", request))

    # Add callback handlers
    dispatcher.add_handler(CallbackQueryHandler(request_confirmation))
    dispatcher.add_handler(CallbackQueryHandler(button_callback))

    # Add message handler
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
