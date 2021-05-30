"""Bot implementation using python-telegram-bot library."""
# pylint: disable=broad-except
import logging
import os
from time import strftime, strptime

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
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def help_fun(update: Update, _: CallbackContext) -> None:
    """Send help-message."""
    update.message.reply_text(
        "/help - Вывод списка доступных команд\n"
        "/sub [Channel1, Channel2, ...] - Подписаться на каналы\n"
        "/unsub [Channel1, Channel2, ...] - Отписаться от каналов\n"
        "/list - Просмотр списка подписок\n"
        "\n"
        "По всем вопросам писать @deanit и @seregaukhin"
    )


def start(update: Update, _: CallbackContext) -> None:
    """Send welcome to a user along with help-message."""
    chat_id = update.message.chat_id
    username = update.message.chat.username
    update.message.reply_text(text=f"Привет, {username}! chat_id = {chat_id}")
    help_fun(update, None)


class TwitchBot(Updater):
    """Main bot class."""

    def __init__(self) -> None:
        """Initialize bot."""
        bot_token = os.environ.get("BOT_TOKEN", None)
        super().__init__(bot_token)
        self.database = Database()
        self.twitch_api = None  # Will be initialized by specific method
        self._add_handlers()

        self.start_polling()

    def _add_handlers(self) -> None:
        self.dispatcher.add_handler(CommandHandler("start", start))
        self.dispatcher.add_handler(CommandHandler("help", help_fun))
        self.dispatcher.add_handler(CommandHandler("list", self.list_subs))

        self.dispatcher.add_handler(CommandHandler("subscribe", self.subscribe))
        self.dispatcher.add_handler(CommandHandler("sub", self.subscribe))
        self.dispatcher.add_handler(CallbackQueryHandler(self.subscribe, pattern="^SUB_QUERY"))

        self.dispatcher.add_handler(CommandHandler("unsubscribe", self.unsubscribe))
        self.dispatcher.add_handler(CommandHandler("unsub", self.unsubscribe))
        self.dispatcher.add_handler(CallbackQueryHandler(self.unsubscribe, pattern="^UNSUB_QUERY"))

        self.dispatcher.add_handler(CommandHandler("unsub_all", self.unsub_all))
        self.dispatcher.add_handler(CommandHandler("list_all", self.list_all))

        self.dispatcher.add_handler(
            CallbackQueryHandler(self.channel_info, pattern="^CHANNEL_INFO_QUERY")
        )

        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    def register_twitch_api(self, twitch_api: TwitchApi) -> None:
        """Register twitch api."""
        self.twitch_api = twitch_api

    def subscribe(self, update: Update, _: CallbackContext) -> None:
        """Bot function handling subscriptions."""
        channels_to_subscribe = update.message.text.split()[1:]

        user_subs = self.database.get_subs_for_user(update.message.chat_id)

        if len(channels_to_subscribe) >= 1:
            for channel in channels_to_subscribe:
                try:
                    twitch_id, display_name = self.twitch_api.get_twitch_user_by_name(channel)
                    if twitch_id == -1:
                        update.message.reply_text(
                            text=f"Канал {channel} не найден."
                        )
                    if twitch_id not in user_subs:
                        self.database.put_subs_for_user(update.message.chat_id, [twitch_id])
                        if len(self.database.get_channel_name(twitch_id)) == 0:
                            self.twitch_api.sub(twitch_id)
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
        """Bot function handling unsubscriptions."""
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
                    twitch_id, display_name = self.twitch_api.get_twitch_user_by_name(channel)
                    if twitch_id in user_subs:
                        self.database.delete_user_sub(chat_id, twitch_id)
                        channel_subs = self.database.get_users_for_sub(twitch_id)
                        if len(channel_subs) == 0:
                            self.database.delete_channel_name(twitch_id)
                            self.twitch_api.unsubscribe_event(twitch_id)
                            # self.twitch_api.unsubscribe(twitch_id)
                        reply_func(f"Успешная отписка от {display_name}!")
                    else:
                        reply_func(f"Вы не подписаны на {display_name}!")
                except Exception as exception:
                    reply_func(f"Возникла ошибка при отписке от {channel}.\nПричина: {exception}")
        else:
            if len(user_subs) > 0:
                channel_names = [
                    self.database.get_channel_name(twitch_id)[0] for twitch_id in user_subs
                ]
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

    def unsub_all(self, update: Update, _:CallbackContext) -> None:
        if update.message.chat_id in [234383022, 456145017]:
            try:
                self.twitch_api.unsubscribe_all()
                update.message.reply_text('Unsubscribed from all')
            except Exception as exception:
                update.message.reply_text(
                    text=f"Возникла ошибка при отписке от всего.\nПричина: {exception}"
                )
        else:
            update.message.reply_text('Command is admin-only')

    def list_all(self, update: Update, _:CallbackContext) -> None:
        if update.message.chat_id in [234383022, 456145017]:
            try:
                data = self.twitch_api.list_all_subscriptions()
                if len(data) == 0:
                    update.message.reply_text("No events")
                else:
                    update.message.reply_text('\n'.join([item['condition']['broadcaster_user_id'] for item in data]))
            except Exception as exception:
                update.message.reply_text(
                    text=f"Возникла ошибка при извлечении полного списка подписок.\nПричина: {exception}"
                )
        else:
            update.message.reply_text('Command is admin-only')

    def list_subs(self, update: Update, _: CallbackContext) -> None:
        """Bot function handling displaying of subscriptions."""
        try:
            result = self.database.get_subs_for_user(update.message.chat_id)
            channel_names = [self.database.get_channel_name(twitch_id)[0] for twitch_id in result]
            if len(result) > 0:
                keyboard = [
                    InlineKeyboardButton(
                        str(channel), callback_data=f"CHANNEL_INFO_QUERY {channel}"
                    )
                    for channel in channel_names
                ]
                keyboard = InlineKeyboardMarkup.from_column(keyboard)
                update.message.reply_text(
                    "Список ваших подписок:\nНажмите, чтобы узнать информацию о канале",
                    reply_markup=keyboard
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

    def channel_info(self, update: Update, _: CallbackContext) -> None:
        """Bot function handling extracting info about channel."""
        channel = update.callback_query.data.split()[1]
        try:
            response = self.twitch_api.check_online(channel)
            data = response['data']
            if len(data) > 0:
                data = data[0]
                starting_time = strftime(
                    "%H:%M",
                    strptime(
                        data['started_at'],
                        "%Y-%m-%dT%H:%M:%SZ"
                    )
                )
                update.callback_query.edit_message_text(
                    f"{channel} стримит {data['game_name']} с {starting_time}!\n"
                    f"{data['title']}\n"
                    "\n"
                    f"https://twitch.tv/{channel}\n"
                )
            else:
                update.callback_query.edit_message_text(
                    f"{channel} не онлайн."
                    "\n"
                    f"https://twitch.tv/{channel}\n"
                )
        except Exception as exception:
            update.callback_query.edit_message_text(
                text=f"Возникла ошибка при извлечении информации о канале.\nПричина: {exception}"
            )
