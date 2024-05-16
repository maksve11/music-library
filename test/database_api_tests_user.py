import sqlite3
import unittest
from .database_api_tests_common import BaseTestCase, db, db_path

class UserDbAPITestCase(BaseTestCase):
    #the strip function removes the tabs generated.
    user1_nickname = 'Robi'
    user1 = {
            "nickname": user1_nickname,
            "password": "pass",
            "age": 18,
            "nationality": "Italy",
            "gender": "Male"
    }
    user2_nickname = 'Joshua'
    user2 = {
            "nickname": user2_nickname,
            "password": "oerae",
            "age": 34,
            "nationality": "Austalia",
            "gender": "Male"
    }
    new_user = {
            "nickname": "sully",
            "password": "ampsy",
    }
    new_user_nickname = 'sully'
    no_user_nickname = 'Nobody'
    initial_size = 3
 
    @classmethod
    def setUpClass(cls):
        print(f"Testing {cls.__name__}")

    def test_users_table_created(self):
        '''
        Checks that the table initially contains 5 users (check 
        musicfinder_data_dump.sql)
        '''
        print(f"({self.test_users_table_created.__name__})", 
              self.test_users_table_created.__doc__)
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'SELECT * FROM users'
        #Connects to the database.
        con = sqlite3.connect(db_path)
        with con:
            #Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            #Provide support for foreign keys
            cur.execute(keys_on)
            #Execute main SQL Statement        
            cur.execute(query1)
            users = cur.fetchall()
            #Assert
            self.assertEqual(len(users), self.initial_size)
        if con:
            con.close()

    def test_create_user_object(self):
        '''
        Check that the method create_user_object works return adequate values
        for the first database row.
        '''
        print(f"({self.test_create_user_object.__name__})", 
              self.test_create_user_object.__doc__)
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM users'
        #Connects to the database.
        con = sqlite3.connect(db_path)
        with con:
            #Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            #Provide support for foreign keys
            cur.execute(keys_on)
            #Execute main SQL Statement        
            cur.execute(query)
            #Extrac the row
            row = cur.fetchone()
            #Test the method
            user = db._create_user_object(row)
            self.assertDictContainsSubset(user, self.user1)

    def test_get_user(self):
        '''
        Test get_user with id Mystery and HockeyFan
        '''
        print(f"({self.test_get_user.__name__})", 
              self.test_get_user.__doc__)
        #Test with an existing user
        user = db.get_user(self.user1_nickname)
        self.assertDictContainsSubset(user, self.user1)
        user = db.get_user(self.user2_nickname)
        self.assertDictContainsSubset(user, self.user2)
 
    def test_get_user_noexistingid(self):
        '''
        Test get_user with id=Nobody
        '''
        print(f"({self.test_get_user_noexistingid.__name__})", 
              self.test_get_user_noexistingid.__doc__)
        #Test with an existing user
        user = db.get_user(self.no_user_nickname)
        self.assertIsNone(user)

    def test_get_users(self):
        '''
        Test that get_users work correctly and extract required user info
        '''
        print(f"({self.test_get_users.__name__})", 
              self.test_get_users.__doc__)
        users = db.get_users()
        #Check that the size is correct
        self.assertEqual(len(users), self.initial_size)
        #Iterate throug users and check if the users with user1_id and
        #user2_id are correct:
        for user in users:
            if user['nickname'] == self.user1_nickname:
                self.assertDictContainsSubset(user, self.user1)
            elif user['nickname'] == self.user2_nickname:
                self.assertDictContainsSubset(user, self.user2)

    def test_delete_user(self):
        '''
        Test that the user Robi is deleted
        '''
        print(f"({self.test_delete_user.__name__})", 
              self.test_delete_user.__doc__)
        resp = db.delete_user(self.user1_nickname)
        self.assertTrue(resp)
        #Check that the users has been really deleted throug a get
        resp2 = db.get_user(self.user1_nickname)
        self.assertIsNone(resp2)
        resp3 = db.get_playlists(self.user1_nickname)
        self.assertEqual(len(resp3), 0)

    def test_delete_user_noexistingnickname(self):
        '''
        Test delete_user with nickname Nobody (no-existing)
        '''
        print(f"({self.test_delete_user_noexistingnickname.__name__})", 
              self.test_delete_user_noexistingnickname.__doc__)
        #Test with an existing user
        resp = db.delete_user(self.no_user_nickname)
        self.assertFalse(resp)

    def test_modify_user(self):
        '''
        Test that the information of the user Roby are changed correctly
        '''
        print(f"({self.test_modify_user.__name__})", 
              self.test_modify_user.__doc__)
        #Get the modified user
        resp = db.modify_user(self.user1_nickname, 78, "Poland", "Male")
        self.assertEqual(resp, self.user1_nickname)
        #Check that the users has been really modified through a get
        resp2 = db.get_user(self.user1_nickname)
        self.assertEqual(resp2['age'],
                          78)
        self.assertEqual(resp2['nationality'], "Poland")
        self.assertEqual(resp2['gender'], "Male")


    def test_modify_user_noexistingnickname(self):
        '''
        Test modify_user with user Nobody (no-existing)
        '''
        print(f"({self.test_modify_user_noexistingnickname.__name__})", 
              self.test_modify_user_noexistingnickname.__doc__)
        #Test with an existing user
        resp = db.modify_user(self.no_user_nickname, "78", "Poland", "Male")
        self.assertIsNone(resp)

    def test_append_user(self):
        '''
        Test that I can add new users
        '''
        print(f"({self.test_append_user.__name__})", 
              self.test_append_user.__doc__)
        nickname = db.append_user(nickname=self.new_user_nickname, password="ampsy" )
        self.assertIsNotNone(nickname)
        self.assertEqual(nickname, self.new_user_nickname)
        resp2 = db.get_user(nickname)
        self.assertDictContainsSubset(self.new_user,
                                      resp2)

    def test_append_existing_user(self):
        '''
        Test that I cannot add two users with the same name
        '''
        print(f"({self.test_append_existing_user.__name__})", 
              self.test_append_existing_user.__doc__)
        nickname = db.append_user(self.user1_nickname, "adas")
        self.assertIsNone(nickname)

if __name__ == '__main__':
    print('Start running tests')
    unittest.main()