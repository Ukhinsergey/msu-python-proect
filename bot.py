#!/usr/bin/env python
# pylint: disable=C0116
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import json
import os

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from flask import request

from database import Database

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def echo(update: Update, _: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


class TwitchBot(Updater):
    """Main bot class"""
    def __init__(self) -> None:
        bot_token = os.environ.get("BOT_TOKEN", None)
        super().__init__(bot_token)
        self.database = Database()
        self._add_handlers()

        self.start_polling()

    def _add_handlers(self) -> None:
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        
        self.dispatcher.add_handler(CommandHandler("subscribe", self.subscribe))
        self.dispatcher.add_handler(CommandHandler("sub", self.subscribe))

        self.dispatcher.add_handler(CommandHandler("unsubscribe", self.unsubscribe))
        self.dispatcher.add_handler(CommandHandler("unsub", self.unsubscribe))

        self.dispatcher.add_handler(CommandHandler("help", self.help))
        self.dispatcher.add_handler(CommandHandler("list_subs", self.list_subs))
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    def help(self, update: Update, _: CallbackContext) -> None:
        update.message.reply_text(
            "/start - Начало работы\n"
            "/subscribe [Channel1, Channel2, ...] - Подписаться на каналы\n"
            "/unsubscribe [Channel1, Channel2, ...] - Отписаться от каналов\n"
            "/sub_list - Просмотр списка подписок"
        )

    def start(self, update: Update, _: CallbackContext) -> None:
        chat_id = update.message.chat_id
        username = update.message.chat.username
        update.message.reply_text(text=f"Привет, {username}! chat_id = {chat_id}")

    def subscribe(self, update: Update, _: CallbackContext) -> None:
        channels_to_subscribe = update.message.text.split()[1:]

        if len(channels_to_subscribe) >= 1:
            for channel in channels_to_subscribe:
                try:
                    # twitch.interface.subscribe_to_channel(channel) # Subscribe to one
                    self.database.put_subs_for_user(update.message.chat_id, channel)
                    update.message.reply_text(
                        text=f"Успешная подписка на {channel}!"
                    )
                except Exception as exception:
                    update.message.reply_text(
                        text=f"Возникла ошибка при подписке на {channel}.\nПричина: {exception}"
                    )
        else:
            update.message.reply_text(
                text="Введите название канала, на который хотите подписаться"
            )

    def unsubscribe(self, update: Update, _: CallbackContext) -> None:
        channels_to_unsubscribe = update.message.text.split()[1:]

        if len(channels_to_unsubscribe) >= 1:
            for channel in channels_to_unsubscribe:
                try:
                    self.database.delete_user_sub(update.message.chat_id, channel)
                    update.message.reply_text(
                        text=f"Успешная отписка от {channel}!"
                    )
                except Exception as exception:
                    update.message.reply_text(
                        text=f"Возникла ошибка при отписке от {channel}.\nПричина: {exception}"
                    )
        else:
            update.message.reply_text(
                text="Введите название канала, от которого хотите отписаться"
            )

    def list_subs(self, update: Update, _: CallbackContext) -> None:
        result = self.database.get_subs_for_user(update.message.chat_id)
        update.message.reply_text(
            text="Подписки: " + '\n'.join(map(str, result))
        )
    
    

        
