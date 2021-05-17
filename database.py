from sqlalchemy import create_engine, text

engine = create_engine('sqlite:///test.db', echo=True, future=True)

with engine.connect() as conn:
    conn.execute(text("CREATE TABLE some_table (x int, y int)"))
    conn.execute(
        text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        [{"x": 1, "y": 1}, {"x": 2, "y": 4}]
    )
    conn.commit()

class Database:
    def __init__(self, table_name='user_subs'):
        """Creates simple wrapper around database with one table
        table_name : str [default='user_subs'] - name of table (ChatID int, TwitchID int)
        """
        self.table_name = table_name
        self.user_colname = 'ChatID'
        self.sub_colname = 'TwitchID'
        self.engine = create_engine('sqlite:///test.db', echo=True, future=True)

        
        # Create table if not exists
        with self.engine.connect() as conn:
            if self.table_name not in self.engine.dialect.get_table_names(conn):
                conn.execute(text(f"CREATE TABLE {self.table_name} ({self.user_colname} int, {self.sub_colname} int)"))
                conn.commit()

    def _get_data(self, data_col, data_value):
        """Get data with the following select
        'SELECT * FROM {self.table_name} WHERE {data_col}={data_value}'
        """
        with self.engine.connect() as conn:
            req = text(f'SELECT * FROM {self.table_name} WHERE {data_col}={data_value}')
            result = [*conn.execute(req)]
        return result
    
    def _put_data(self, data_cols, data_values):
        with engine.connect() as conn:
            conn.execute(
                text(f"INSERT INTO {self.table_name} ({', '.join(data_cols)}) VALUES ({':'+', :'.join(data_cols)})"),
                [dict(zip(data_cols, values)) for values in data_values]
            )
            conn.commit()

    def _delete_on_cond(self, condition):
        with engine.connect() as conn:
            conn.execute(text(f"DELETE FROM {self.table_name} WHERE {condition}"))
            conn.commit()

    def get_subs_for_user(self, chat_id):
        """Get list of subscriptions for user 'chat_id'"""
        result = self._get_data(self.user_colname, chat_id)
        return [cur[1] for cur in result]

    def get_users_for_sub(self, twitch_id):
        """Get list of users subscribed for twitch channel with 'twitch_id'"""
        result = self._get_data(self.sub_colname, twitch_id)
        return [cur[0] for cur in result]
    
    def put_subs_for_user(self, chat_id, twitch_ids):
        """Put list of subscriptions 'twitch_ids' for user 'chat_id'"""
        self._put_data(
            [self.user_colname, self.sub_colname],
            [(chat_id,twitch_id) for twitch_id in twitch_ids]
        )


    def delete_all_user_subs(self, chat_id):
        self._delete_on_cond(f"{self.user_colname}={chat_id}")
    
    def delete_user_sub(self, chat_id, twitch_id):
        self._delete_on_cond(f"{self.user_colname}={chat_id} AND {self.sub_colname}={twitch_id}")