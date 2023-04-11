import logging
import random
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters

# Logging
logging.basicConfig(level=logging.INFO)

# Colocar o API token do BotFather
API_TOKEN = "YOUR_API_TOKEN"

# Armazena os dados do clube do livro, como títulos, encontros e citações de cada livro.
book_club_data = {
    "book_1": {
        "title": "O Grande Divórcio",
        "schedule": "Próximos encontros:",
        "meetings": [
            datetime.date(15, 4, 2023),
            datetime.date(22, 4, 2023),
            # Add more meeting dates if needed
        ],
        "quotes": ["Book 1 Quote 1", "Book 1 Quote 2", "Book 1 Quote 3"],
    },
    "book_2": {
        "title": "Antônio e Cleópatra",
        "schedule": "Próximos encontros:",
        "meetings": [
            datetime.date(13, 5, 2023),
            # Add more meeting dates if needed
        ],
        "quotes": ["Book 2 Quote 1", "Book 2 Quote 2", "Book 2 Quote 3"],
    },
    "book_3": {
        "title": "O Auto da Compadecida",
        "schedule": "Próximos encontros:",
        "meetings": [
            datetime.date(27, 5, 2023),
            # Add more meeting dates if needed
        ],
        "quotes": ["Book 2 Quote 1", "Book 2 Quote 2", "Book 2 Quote 3"],
    },
}

# Inicio do bot, envia os comandos para escolher um livro
def start(update: Update, _: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("O Grande Divórcio", callback_data="book_1"), InlineKeyboardButton("Antônio e Cleópatra", callback_data="book_2"), InlineKeyboardButton("O Auto da Compadecida ", callback_data="book_3")],
        [InlineKeyboardButton("Ajuda", callback_data="help")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Escolha o livro para saber mais:", reply_markup=reply_markup)

# Mostra a seleção de um livro e envia as opções (agenda, próximo encontro, citação)
def book_info(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    book_id = query.data
    book = book_club_data[book_id]

    keyboard = [
        [InlineKeyboardButton("Encontros", callback_data=f"{book_id}_schedule")],
        [InlineKeyboardButton("Próximos encontro", callback_data=f"{book_id}_next_meeting")],
        [InlineKeyboardButton("Frase do livro", callback_data=f"{book_id}_quote")],
        [InlineKeyboardButton("Voltar", callback_data="back")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(f"Escolha: {book['title']}. Escolha uma opção:", reply_markup=reply_markup)

# Exibe os dados do livro escolhido
def handle_book_data(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    book_id, data_type = query.data.split("_")
    book = book_club_data[book_id]

    if data_type == "quote":
        data = random.choice(book["quotes"])
    elif data_type == "next_meeting":
        today = datetime.date.today()
        next_meeting = min(meeting for meeting in book["meetings"] if meeting > today)
        data = next_meeting.strftime("%d-%m-%Y")
    else:
        data = book[data_type]

    query.edit_message_text(f"{book['title']} {data_type.capitalize()}: {data}")

# Volta para as opções
def back(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    start(query, context)

# Explica o bot pra Bárbara, que não entendeu nada
def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Você pode interagir com este bot usando o teclado ou com os comandos:\n"
         "- @bot Livro X Encontros\n"
         "- @bot Livro Y Próximo encontro\n"
    )

# Aciona os comandos de selecionar um livro e exibe os dados
def handle_text(update: Update, context: CallbackContext):
    text = update.message.text.lower()
    book_id, data_type = None, None

    if "book 1" in text:
        book_id = "book_1"
    elif "book 2" in text:
        book_id = "book_2"

    if "schedule" in text:
        data_type = "schedule"
    elif "next meeting" in text:
        data_type = "next_meeting"
    elif "quote" in text:
        data_type = "quote"

    if book_id and data_type:
        book = book_club_data[book_id]

        if data_type == "quote":
            data = random.choice(book["quotes"])
        elif data_type == "next_meeting":
            today = datetime.date.today()
            next_meeting = min(meeting for meeting in book["meetings"] if meeting > today)
            data = next_meeting.strftime("%d-%m-%Y")
        else:
            data = book[data_type]

        update.message.reply_text(f"{book['title']} {data_type.capitalize()}: {data}")
    else:
        update.message.reply_text("Comando inválido. Por favor, use um dos comandos ou o teclado.")

# Aciona os handlers de todos os comandos do bot e inicia o bot
def main():
    updater = Updater(API_TOKEN)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(book_info, pattern="^book_[12]$"))
    dispatcher.add_handler(CallbackQueryHandler(handle_book_data, pattern="^book_[12]_(schedule|next_meeting|quote)$"))
    dispatcher.add_handler(CallbackQueryHandler(back, pattern="^back$"))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
