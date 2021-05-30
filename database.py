"""Database wrapper for storing subscriptions and channel names."""
# pylint: disable=line-too-long

import os
from typing import List, Tuple

from sqlalchemy import create_engine, text


class Database:
    """Main database class."""

    def __init__(self, subs_table='user_subs', tw_channels_table='twitch_channels', echo=True):
        """Create simple wrapper around database with one table.

        subs_table        : str - name of table (ChatID int, TwitchID int)
        tw_channels_table : str - name of table (TwitchID int, ChannelName str)
        """
        self.subs_table = subs_table
        self.tw_channels_table = tw_channels_table

        self.user_colname = 'ChatID'
        self.sub_colname = 'TwitchID'
        self.channel_colname = 'ChannelName'

        self.engine = create_engine(
            os.environ.get('DATABASE_URL', 'sqlite:///test.db').replace('postgres', 'postgresql'),
            echo=echo, future=True
        )

        # Create tables if not exists
        with self.engine.connect() as conn:
            if self.subs_table not in self.engine.dialect.get_table_names(conn):
                conn.execute(text(f'CREATE TABLE {self.subs_table} ({self.user_colname} int, {self.sub_colname} int)'))
            if self.tw_channels_table not in self.engine.dialect.get_table_names(conn):
                conn.execute(text(f'CREATE TABLE {self.tw_channels_table} ({self.sub_colname} int, {self.channel_colname} varchar)'))
            conn.commit()

    # Internal functions
    def _get_data(self, table_name: str, data_col: str, data_value: object) -> List[object]:
        """Get data with the simple SQL select.

        SQL query:
        'SELECT * FROM {table_name} WHERE {data_col}={data_value}'
        """
        with self.engine.connect() as conn:
            req = text(f'SELECT * FROM {table_name} WHERE {data_col}={data_value}')
            result = [*conn.execute(req)]
        return result

    def _put_data(self, table_name: str, data_cols: Tuple[str, str], data_values: List[Tuple[object, object]]) -> None:
        """Put data with the simple SQL insert.

        SQL query:
        'INSERT INTO {table_name} (data_cols) VALUES (:data_values)'
        """
        with self.engine.connect() as conn:
            conn.execute(
                text(f"INSERT INTO {table_name} ({', '.join(data_cols)}) VALUES ({':'+', :'.join(data_cols)})"),
                [dict(zip(data_cols, values)) for values in data_values]
            )
            conn.commit()

    def _delete_on_cond(self, table_name: str, condition: str) -> None:
        """Delete data with the simple SQL delete.

        SQL query:
        'DELETE FROM {table_name} WHERE {condition}'
        """
        with self.engine.connect() as conn:
            conn.execute(text(f'DELETE FROM {table_name} WHERE {condition}'))
            conn.commit()

    # Get functions
    def get_subs_for_user(self, chat_id: int) -> List[int]:
        """Get list of subscriptions for user 'chat_id'."""
        result = self._get_data(self.subs_table, self.user_colname, chat_id)
        return [cur[1] for cur in result]

    def get_users_for_sub(self, twitch_id: int) -> List[int]:
        """Get list of users subscribed for twitch channel with 'twitch_id'."""
        result = self._get_data(self.subs_table, self.sub_colname, twitch_id)
        return [cur[0] for cur in result]

    def get_channel_name(self, twitch_id: int) -> List[str]:
        """Get list of channel names for 'twitch_id'."""
        result = self._get_data(self.tw_channels_table, self.sub_colname, twitch_id)
        return [cur[1] for cur in result]

    # Put functions
    def put_subs_for_user(self, chat_id: int, twitch_ids: List[int]) -> None:
        """Put list of subscriptions 'twitch_ids' for user 'chat_id'."""
        self._put_data(
            self.subs_table,
            [self.user_colname, self.sub_colname],
            [(chat_id, twitch_id) for twitch_id in twitch_ids]
        )

    def put_channel_name(self, twitch_id: int, channel_name: str) -> None:
        """Register 'channel_name' for 'twitch_id'."""
        self._put_data(
            self.tw_channels_table,
            [self.sub_colname, self.channel_colname],
            [(twitch_id, channel_name)]
        )

    # Delete functions
    def delete_user_sub(self, chat_id: int, twitch_id: int) -> None:
        """Remove ('chat_id', 'twitch_id') pair from subscriptions."""
        self._delete_on_cond(
            self.subs_table,
            f'{self.user_colname}={chat_id} AND {self.sub_colname}={twitch_id}'
        )

    def delete_channel_name(self, twitch_id: int) -> None:
        """Remove channel name for 'twitch_id'."""
        self._delete_on_cond(
            self.tw_channels_table,
            f'{self.sub_colname}={twitch_id}'
        )
