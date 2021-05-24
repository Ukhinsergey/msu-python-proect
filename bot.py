"""
Bot implementation using python-telegram-bot library
"""

import logging
import os
import random

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    CallbackQueryHandler
)

from database import Database
from twitch import TwitchApi

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def echo(update: Update, _: CallbackContext) -> None:
    """Echo the user message"""
    update.message.reply_text(update.message.text)


class TwitchBot(Updater):
    """Main bot class"""
    def __init__(self) -> None:
        bot_token = os.environ.get("BOT_TOKEN", None)
        super().__init__(bot_token)
        self.database = Database()
        self.twitch_api = TwitchApi()
        self._add_handlers()

        self.start_polling()

    def _add_handlers(self) -> None:
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("help", self.help))
        self.dispatcher.add_handler(CommandHandler("list", self.list_subs))

        self.dispatcher.add_handler(CommandHandler("subscribe", self.subscribe))
        self.dispatcher.add_handler(CommandHandler("sub", self.subscribe))
        self.dispatcher.add_handler(CallbackQueryHandler(self.subscribe, pattern="^SUB_QUERY"))

        self.dispatcher.add_handler(CommandHandler("unsubscribe", self.unsubscribe))
        self.dispatcher.add_handler(CommandHandler("unsub", self.unsubscribe))
        self.dispatcher.add_handler(CallbackQueryHandler(self.unsubscribe, pattern="^UNSUB_QUERY"))

        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    def help(self, update: Update, _: CallbackContext) -> None:
        """Send help-message"""
        update.message.reply_text(
            "/start - Начало работы\n"
            "/help - Вывод списка доступных команд\n"
            "/sub [Channel1, Channel2, ...] - Подписаться на каналы\n"
            "/unsub [Channel1, Channel2, ...] - Отписаться от каналов\n"
            "/list - Просмотр списка подписок\n"
            "\n"
            "По всем вопросам писать @deanit и @seregaukhin"
        )

    def start(self, update: Update, _: CallbackContext) -> None:
        """Send welcome to a user along with help-message"""
        chat_id = update.message.chat_id
        username = update.message.chat.username
        update.message.reply_text(text=f"Привет, {username}! chat_id = {chat_id}")
        self.help(update, None)

    def subscribe(self, update: Update, _: CallbackContext) -> None:
        """Bot function handling subscriptions"""
        channels_to_subscribe = update.message.text.split()[1:]

        user_subs = self.database.get_subs_for_user(update.message.chat_id)

        if len(channels_to_subscribe) >= 1:
            for channel in channels_to_subscribe:
                try:
                    # display_name, twitch_id = channel, random.randint(0, 999999)
                    twitch_id, display_name = self.twitch_api.get_twitch_user_by_name(channel) # Subscribe to one
                    if twitch_id not in user_subs:
                        self.database.put_subs_for_user(update.message.chat_id, [twitch_id])
                        self.database.put_channel_name(twitch_id, display_name)
                        update.message.reply_text(f"Успешная подписка на {display_name}!")
                    else:
                        update.message.reply_text(f"Вы уже подписаны на {display_name}!")
                except Exception as exception:
                    update.message.reply_text(
                        text=f"Возникла ошибка при подписке на {channel}.\nПричина: {exception}"
                    )
        else:
            update.message.reply_text(
                text="Вы должны ввести название канала, на который хотите подписаться"
            )

    def unsubscribe(self, update: Update, _: CallbackContext) -> None:
        """Bot function handling unsubscriptions"""
        if update.message is not None:
            channels_to_unsubscribe = update.message.text.split()[1:]
            chat_id = update.message.chat_id
            reply_func = update.message.reply_text
        else:
            channels_to_unsubscribe = update.callback_query.data.split()[1:]
            chat_id = update.callback_query.message.chat_id
            reply_func = update.callback_query.edit_message_text

        user_subs = self.database.get_subs_for_user(chat_id)

        if len(channels_to_unsubscribe) >= 1:
            for channel in channels_to_unsubscribe:
                try:
                    # display_name, twitch_id = channel, self.database._get_data(self.database.tw_channels_table, self.database.channel_colname, channel)[0]
                    twitch_id, display_name = self.twitch_api.get_twitch_user_by_name(channel)
                    if twitch_id in user_subs:
                        self.database.delete_user_sub(chat_id, twitch_id)
                        reply_func(f"Успешная отписка от {display_name}!")
                    else:
                        reply_func(f"Вы не подписаны на {display_name}!")
                except Exception as exception:
                    reply_func(f"Возникла ошибка при отписке от {channel}.\nПричина: {exception}")
        else:
            if len(user_subs) > 0:
                channel_names = [self.database.get_channel_name(twitch_id)[0] for twitch_id in user_subs]
                keyboard = [
                    InlineKeyboardButton(
                        str(channel), callback_data=f"UNSUB_QUERY {channel}"
                    )
                    for channel in channel_names
                ]
                keyboard = InlineKeyboardMarkup.from_column(keyboard)
                reply_func(
                    "Выберите канал, от которого хотите отписаться:",
                    reply_markup=keyboard
                )
            else:
                reply_func(
                    "У вас еще нет подписок!\n"
                    "Чтобы подписаться, воспользуйтесь командой\n"
                    "/sub <Название канала>"
                )


    def list_subs(self, update: Update, _: CallbackContext) -> None:
        """Bot function handling displaying of subscriptions"""
        try:
            result = self.database.get_subs_for_user(update.message.chat_id)
            channel_names = [self.database.get_channel_name(twitch_id)[0] for twitch_id in result]
            if len(result) > 0:
                update.message.reply_text(
                    text="Ваши подписки:\n" +
                    "\n".join(map(str, zip(result, channel_names)))
                )
            else:
                update.message.reply_text(
                    "У вас еще нет подписок!\n"
                    "Чтобы подписаться, воспользуйтесь командой\n"
                    "/sub <Название канала>"
                )

        except Exception as exception:
            update.message.reply_text(
                text=f"Возникла ошибка при извлечении списка подписок.\nПричина: {exception}"
            )
