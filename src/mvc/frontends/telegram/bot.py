from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    ContextTypes,
)

from mvc.config import TELEGRAM_BOT_TOKEN

class Bot:
    def __init__(self) -> None:
        self.screaming = False

        next_button = InlineKeyboardButton(text="Next", callback_data="next")
        back_button = InlineKeyboardButton(text="Back", callback_data="back")
        url_button = InlineKeyboardButton(
            text="Tutorial",
            url="https://core.telegram.org/bots/api",
        )

        self.keyboard_m1 = InlineKeyboardMarkup([[next_button]])
        self.keyboard_m2 = InlineKeyboardMarkup([[back_button], [url_button]])

    def get_bot_username(self) -> str:
        return "TutorialBot"

    def get_bot_token(self) -> str:
        return TELEGRAM_BOT_TOKEN

    async def on_update_received(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        if update.callback_query:
            query = update.callback_query
            await self.button_tap(
                id=query.from_user.id,
                query_id=query.id,
                data=query.data,
                msg_id=query.message.message_id,
                context=context,
            )
            return

        if not update.message:
            return

        msg = update.message
        user = msg.from_user
        id_ = user.id

        print(f"{user.first_name} wrote {msg.text}")

        txt = msg.text
        if msg.text and msg.text.startswith("/"):
            if txt == "/scream":
                self.screaming = True
            elif txt == "/whisper":
                self.screaming = False
            elif txt == "/menu":
                await self.send_menu(id_, "<b>Menu 1</b>", self.keyboard_m1, context)
            return

        if self.screaming:
            await self.scream(id_, msg, context)
        else:
            await self.copy_message(id_, msg.message_id, context)

    async def send_text(
        self,
        who: int,
        what: str,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        await context.bot.send_message(chat_id=who, text=what)

    async def copy_message(
        self,
        who: int,
        msg_id: int,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        await context.bot.copy_message(
            from_chat_id=who,
            chat_id=who,
            message_id=msg_id,
        )

    async def scream(
        self,
        id_: int,
        msg,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        if msg.text:
            await self.send_text(id_, msg.text.upper(), context)
        else:
            await self.copy_message(id_, msg.message_id, context)

    async def send_menu(
        self,
        who: int,
        txt: str,
        kb: InlineKeyboardMarkup,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        await context.bot.send_message(
            chat_id=who,
            text=txt,
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
        )

    async def button_tap(
        self,
        id: int,
        query_id: str,
        data: str,
        msg_id: int,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        if data == "next":
            new_txt = "MENU 2"
            new_kb = self.keyboard_m2
        elif data == "back":
            new_txt = "MENU 1"
            new_kb = self.keyboard_m1
        else:
            return

        await context.bot.answer_callback_query(callback_query_id=query_id)
        await context.bot.edit_message_text(
            chat_id=id,
            message_id=msg_id,
            text=new_txt,
        )
        await context.bot.edit_message_reply_markup(
            chat_id=id,
            message_id=msg_id,
            reply_markup=new_kb,
        )
