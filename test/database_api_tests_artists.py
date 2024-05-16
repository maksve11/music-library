import sqlite3
import unittest
from .database_api_tests_common import BaseTestCase, db, db_path

class ArtistsDbAPITestCase(BaseTestCase):

    artist1 = {'legalName': 'Placebo',
               'genre': 'Alternative Rock',
               'foundingLocation': "England",
               'language': "English",
               'foundingDate': 1996
               }
    artist2 = {
            'legalName': 'Editors',
            'genre': 'Indie Rock',
            'foundingLocation': "England",
            'language': "English",
            'foundingDate': 2004
            }
    initial_size = 20

    @classmethod
    def setUpClass(cls):
        print(f"Testing {cls.__name__}")

    def test_artists_table_created(self):
        print(f"({self.test_artists_table_created.__name__})", 
              self.test_artists_table_created.__doc__)
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM artists'
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
            artists = cur.fetchall()
            #Assert
            self.assertEqual(len(artists), self.initial_size)
        if con:
            con.close()

    def test_create_artist_object(self):
        '''
        Check that the method _create_artist_object works return adequate
        values for the first database row.
        '''
        print(f"({self.test_create_artist_object.__name__})", 
              self.test_create_artist_object.__doc__)
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM artists WHERE legalName = "Placebo"'
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
            artist = db._create_artist_object(row)
            self.assertDictContainsSubset(artist, self.artist1)

    def test_get_artist(self):
        '''
        Test get_artist 
        '''
        print(f"({self.test_get_artist.__name__})", 
              self.test_get_artist.__doc__)
        #Test with an existing artist
        a = db.get_artist(self.artist1['legalName'])
        self.assertDictContainsSubset(a, self.artist1)


    def test_get_noexistingartist(self):
        '''
        Test get_artist with msg-200 (no-existing)
        '''
        print(f"({self.test_get_noexistingartist.__name__})", 
              self.test_get_noexistingartist.__doc__)
        #Test with an existing artist
        a = db.get_artist("NoExisting")
        self.assertIsNone(a)

    def test_get_artists(self):
        '''
        Test that get_artists work correctly
        '''
        print(f"({self.test_get_artists.__name__})", 
              self.test_get_artists.__doc__)
        artists = db.get_artists()
        #Check that the size is correct
        self.assertEqual(len(artists), self.initial_size)
        #Iterate through artists and check if the artists with artist1_id are correct:
        for artist in artists:
            if artist['legalName'] == self.artist1['legalName']:
                self.assertDictContainsSubset(artist, self.artist1)

    def test_get_artists_specific_genre(self):
        '''
        Get all artists with genre containing the word 'rock'.
        '''
        #artists sent from Mystery are 13 and 14
        print(f"({self.test_get_artists_specific_genre.__name__})", 
              self.test_get_artists_specific_genre.__doc__)
        artists = db.get_artists(genre = 'Indie Rock')
        self.assertEqual(len(artists), 3)
        #artists id are 13 and 14
        for artist in artists:
            self.assertIn(artist['legalName'], ('Editors', 'Foals', 'Empire of the sun'))
            self.assertNotIn(artist['legalName'], ('Clap Clap'))

    def test_create_artist(self):
        '''
        Test that a new artist can be created
        '''
        print(f"({self.test_create_artist.__name__})", 
              self.test_create_artist.__doc__)
        artistid = db.create_artist("Oasis","Pop","England","English",2004)
        self.assertIsNotNone(artistid)
        #Get the expected modified artist
        new_artist = {}
        new_artist['legalName'] = 'Editors'
        new_artist['genre'] = 'Indie Rock'
        new_artist['foundingLocation'] = 'England'
        new_artist['language'] = 'English'
        new_artist['foundingDate'] = 2004


        #Check that the artists has been really modified through a get
        resp2 = db.get_artist("Editors")
        self.assertDictContainsSubset(new_artist, resp2)

if __name__ == '__main__':
    print('Start running tests')
    unittest.main()