from telegram.ext import Application, CallbackQueryHandler, MessageHandler, filters

from mvc.frontends.telegram.bot import Bot

def main():
    bot = Bot()

    application = Application.builder().token(bot.get_bot_token()).build()

    application.add_handler(CallbackQueryHandler(bot.on_update_received))
    application.add_handler(MessageHandler(filters.ALL, bot.on_update_received))

    application.run_polling()


if __name__ == "__main__":
    main()
