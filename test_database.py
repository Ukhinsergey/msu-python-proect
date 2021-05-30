import unittest
from database import Database
import os

class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.database = Database(echo = False)

    def test_get_data_empty_subsdb(self):
        result = self.database._get_data(self.database.subs_table, self.database.user_colname, 1)
        self.assertEqual(result, [], 'test_get_data_empty_subsdb')

    def test_get_data_empty_tw_channelsdb(self):
        result = self.database._get_data(self.database.tw_channels_table, self.database.sub_colname, 1)
        self.assertEqual(result, [], 'test_get_data_empty_tw_channelsdb')

    def test_get_data_put_and_get_subsdb(self):
        self.database._put_data(
            self.database.subs_table,
            [self.database.user_colname, self.database.sub_colname],
            [(1, 2)]
        )
        result = self.database._get_data(self.database.subs_table, self.database.user_colname, 1)
        self.assertEqual(result, [(1, 2)])

    def test_get_data_put_and_get_tw_channelsdb(self):
        self.database._put_data(
            self.database.tw_channels_table,
            [self.database.sub_colname, self.database.channel_colname],
            [(1, "zdarova")]
        )
        result = self.database._get_data(self.database.tw_channels_table, self.database.sub_colname, 1)
        self.assertEqual(result, [(1, 'zdarova')])

    def test_get_data_put_and_getwrong_subsdb(self):
        self.database._put_data(
            self.database.subs_table,
            [self.database.user_colname, self.database.sub_colname],
            [(1, 2)]
        )
        result = self.database._get_data(self.database.subs_table, self.database.user_colname, 2)
        self.assertEqual(result, [])

    def test_get_data_put_and_getwrong_tw_channelsdb(self):
        self.database._put_data(
            self.database.tw_channels_table,
            [self.database.sub_colname, self.database.channel_colname],
            [(1, "zdarova")]
        )
        result = self.database._get_data(self.database.tw_channels_table, self.database.sub_colname, 2)
        self.assertEqual(result, [])

    def test_delete_on_cond_subs(self):
        self.database._put_data(
            self.database.subs_table,
            [self.database.user_colname, self.database.sub_colname],
            [(1, 2)]
        )
        self.database._put_data(
            self.database.subs_table,
            [self.database.user_colname, self.database.sub_colname],
            [(11, 22)]
        )
        self.database._delete_on_cond(
            self.database.subs_table,
            f"{self.database.user_colname}=1 AND {self.database.sub_colname}=2"
        )
        result = self.database._get_data(self.database.subs_table, self.database.user_colname, 1)
        self.assertEqual(result, [])
        result = self.database._get_data(self.database.subs_table, self.database.user_colname, 11)
        self.assertEqual(result, [(11, 22)])

    def test_delete_on_cond_tw_channels(self):
        self.database._put_data(
            self.database.tw_channels_table,
            [self.database.sub_colname, self.database.channel_colname],
            [(1, "zdarova")]
        )
        self.database._put_data(
            self.database.tw_channels_table,
            [self.database.sub_colname, self.database.channel_colname],
            [(11, "poka")]
        )
        self.database._delete_on_cond(
            self.database.tw_channels_table,
            f"{self.database.sub_colname}=11"
        )
        result = self.database._get_data(self.database.tw_channels_table, self.database.sub_colname, 1)
        self.assertEqual(result, [(1, "zdarova")])
        result = self.database._get_data(self.database.tw_channels_table, self.database.sub_colname, 11)
        self.assertEqual(result, [])

    def test_1_rest_functions(self):
        self.database.put_subs_for_user(1, [1,2,3,4,5,6,7,8,9,10])
        self.database.put_subs_for_user(2, [13,22,31,44,5,6,7,8,9,10])
        self.database.put_channel_name(1, '1')
        self.database.put_channel_name(2, '2')
        self.database.put_channel_name(3, '3')
        self.database.put_channel_name(5, '5')
        self.database.put_channel_name(4, '4')
        self.database.put_channel_name(22, '22')
        self.database.put_channel_name(31, '31testchannel')
        self.database.put_channel_name(44, '44')
        self.database.put_channel_name(13, '13')
        self.database.put_channel_name(10, '10')
        self.database.put_channel_name(9, '9')
        self.database.put_channel_name(8, '8')
        self.database.put_channel_name(7, '7')
        self.database.put_channel_name(6, '6')
        result = self.database.get_subs_for_user(1)
        self.assertEqual(result, [1,2,3,4,5,6,7,8,9,10])
        result = self.database.get_subs_for_user(2)
        self.assertEqual(result, [13,22,31,44,5,6,7,8,9,10])
        result = self.database.get_users_for_sub(22)
        self.assertEqual(result, [2])
        result = self.database.get_users_for_sub(7)
        self.assertEqual(result, [1, 2])
        result = self.database.get_channel_name(31)
        self.assertEqual(result, ['31testchannel'])
        self.database.delete_user_sub(1, 3)
        result = self.database.get_subs_for_user(1)
        self.assertEqual(result, [1,2,4,5,6,7,8,9,10])
        self.database.delete_channel_name(44)
        result = self.database.get_channel_name(44)
        self.assertEqual(result, [])
        result = self.database.get_subs_for_user(2)
        self.assertEqual(result, [13,22,31,44,5,6,7,8,9,10])



    def tearDown(self):
        os.remove('test.db')



if __name__ == '__main__':
    unittest.main()