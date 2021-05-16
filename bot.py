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

        self._add_handlers()

        self.start_polling()

        # port = int(os.environ.get("PORT", 443))
        # base_url = os.environ.get("APP_URL")
        # url_path = os.environ.get("TELEGRAM_WH")
        # self.start_webhook(
        #     listen="0.0.0.0", 
        #     port=port,
        #     url_path=url_path,
        #     webhook_url=base_url+url_path
        # )


    def _add_handlers(self) -> None:
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("subscribe", self.subscribe))
        self.dispatcher.add_handler(CommandHandler("help", self.help))
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

        if len(channels_to_subscribe) > 1:
            for channel in channels_to_subscribe:
                try:
                    twitch.interface.subscribe_to_channel(channel) # Subscribe to one
                    # add to database
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


# def main() -> None:
#     """Start the bot."""

#     bot = TwitchBot('./config')

#     # Start the Bot
#     bot.start_polling()
#     bot.idle()


# if __name__ == '__main__':
#     main()
