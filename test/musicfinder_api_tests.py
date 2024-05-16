import unittest, copy
import json

import flask

import resources as resources
import database

db_path ='db/db_test.db'
db = database.MusicDatabase(db_path)
initial_artists = 20
initial_users = 3
resources.app.config['TESTING'] = True
resources.app.config['DATABASE'] = db

class ResourcesAPITestCase(unittest.TestCase):
    def setUp(self):
        db.load_init_values()
        self.client = resources.app.test_client()

    def tearDown(self):
        db.clean()

class ArtistsTestCase(ResourcesAPITestCase):
    url = '/musicfinder/api/artists/'
    
    @classmethod
    def setUpClass(cls):
        print(f"Testing ArtistsTestCase")
    
    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        print(f"({self.test_url.__name__})", self.test_url.__doc__)
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEqual(view_point, resources.Artists)
    
    def test_get_artists(self):
        '''
        Checks that GET Artists return correct status code and data format
        '''
        print(f"({self.test_get_artists.__name__})", self.test_get_artists.__doc__)
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEqual(resp.status_code, 200)
            data = json.loads(resp.data)
            template = data['collection']['template']
            template_data = template['data']
            self.assertEqual(template_data['name'],'legalName')
            self.assertEqual(template_data['name'],'foundingLocation')
            self.assertEqual(template_data['name'],'genre')
            self.assertEqual(template_data['name'],'language')
            self.assertEqual(template_data['name'],'foundingDate')
            artists = data['collection']['items']
            self.assertEqual(len(artists), initial_artists)

class UsersTestCase(ResourcesAPITestCase):
    url = '/musicfinder/api/users/'
    
    @classmethod
    def setUpClass(cls):
        print(f"Testing UsersTestCase")
    
    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        print(f"({self.test_url.__name__})", self.test_url.__doc__)
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEqual(view_point, resources.Users)
    
    def test_get_users(self):
        '''
        Checks that GET users return correct status code and data format
        '''
        print(f"({self.test_get_users.__name__})", self.test_get_users.__doc__)
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEqual(resp.status_code, 200)
            data = json.loads(resp.data)
            link = data['collection']['links']
            self.assertEqual(link['prompt'],'List of all artists in the Finder')
            self.assertEqual(link['rel'],'artists-all')
            self.assertEqual(link['href'],resources.api.url_for(resources.Artists))
            users = data['collection']['items']
            self.assertEqual(len(users), initial_users)

class ArtistTestCase(ResourcesAPITestCase):
    url = '/musicfinder/api/artists/Placebo/'
    url_wrong = '/musicfinder/api/artists/PlaceboXYZ/'
    artist1 = 'Test'
    artist2 = 'Elio'
    url1 = '/musicfinder/api/artists/%s/'% artist1
    url2 = '/musicfinder/api/artists/'
    artist = {"template":{"data":[{"name":"legalName","value":"Elio"},{"name":"foundingLocation","value":"England"},{"name":"language","value":"english"},{"name":"genre","value":"rock"},
                {"name":"foundingDate","value":1996}]}}

    @classmethod
    def setUpClass(cls):
        print(f"Testing ArtistTestCase")
    
    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        print(f"({self.test_url.__name__})", self.test_url.__doc__)
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEqual(view_point, resources.Artist)
    
    def test_wrong_url(self):
        '''
        Checks that GET Artist return correct status code if given a wrong url
        '''
        resp = self.client.get(self.url_wrong)
        self.assertEqual(resp.status_code, 404)
    
    def test_get_artist(self):
        '''
        Checks that GET Artist return correct status code and data format
        '''
        print(f"({self.test_get_artist.__name__})", self.test_get_artist.__doc__)
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEqual(resp.status_code, 200)
            data = json.loads(resp.data)
            links = data['_links']
            self.assertEqual(len(links), 3)
            for attribute in ('legalName', 'language', 'foundingLocation', 'genre'):
                self.assertIn(attribute, data)

    def test_add_artist(self):
        '''
        Checks that the artist is added correctly

        '''
        print(f"({self.test_add_artist.__name__})", self.test_add_artist.__doc__)
        resp = self.client.post(self.url2, data=json.dumps(self.artist), headers={"Content-Type":"application/json"})
        self.assertEqual(resp.status_code, 201)
        self.assertIn('Location', resp.headers)
        resp2 = self.client.get(self.url2)
        self.assertEqual(resp2.status_code, 200)

    def test_add_wrong_artist(self):
        '''
        Try to add an artist sending wrong data
        '''
        print(f"({self.test_add_wrong_artist.__name__})", self.test_add_wrong_artist.__doc__)
        resp = self.client.post(self.url2, data=json.dumps({"template":{"data":[{"name":"language","value":"english"},{"name":"genre","value":"rock"}]}}), headers={"Content-Type":"application/json"})
        self.assertEqual(resp.status_code, 400)
        
class UserTestCase(ResourcesAPITestCase):
    user1 = 'Test'
    user2 = 'Clayton'
    url1 = '/musicfinder/api/users/%s/'% user1
    url2 = '/musicfinder/api/users/%s/'% user2
    url_wrong = '/musicfinder/api/users/unknown/'


    @classmethod
    def setUpClass(cls):
        print(f"Testing UserTestCase")


    def setUp(self):
        super(UserTestCase,self).setUp()
        self.url = '/musicfinder/api/users/'
        self.user = {"template":{"data":[{"name":"nickname","value":"Clayton"},{"name":"password","value":"frank"},{"name":"age","value":30},{"name":"nationality","value":"England"},
                {"name":"gender","value":"Male"}]}}


    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        print(f"({self.test_url.__name__})", self.test_url.__doc__)
        with resources.app.test_request_context(self.url1):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEqual(view_point, resources.User)


    def test_wrong_url(self):
        '''
        Checks that GET User return correct status code if given a wrong url
        '''
        print(f"({self.test_wrong_url.__name__})", self.test_wrong_url.__doc__)
        resp = self.client.get(self.url_wrong)
        self.assertEqual(resp.status_code, 404)


    def test_get_format(self):
        '''
        Checks that the format of user is correct

        '''
        print(f"({self.test_get_format.__name__})", self.test_get_format.__doc__)
        resp = self.client.get(self.url2)
        data = json.loads(resp.data)
        self.assertIn('_links', data)
        self.assertIn('nickname', data)
        self.assertIn('nationality', data)
        self.assertIn('gender', data)
        self.assertIn('age', data)
        for attribute in ('curies', 'self', 'collection'):
            self.assertIn(attribute, data['_links'])


    def test_add_user(self):
        '''
        Checks that the user is added correctly

        '''
        print(f"({self.test_add_user.__name__})", self.test_add_user.__doc__)
        resp = self.client.put(self.url2, data=json.dumps(self.user), headers={"Content-Type":"application/json"})
        self.assertEqual(resp.status_code, 204) 
        resp2 = self.client.get(self.url2)
        self.assertEqual(resp2.status_code, 200)

class PlaylistTestCase(ResourcesAPITestCase):
    url = '/musicfinder/api/users/robi/playlists/Posted/'
    links_number = 3
    template_data_number = 3


    @classmethod
    def setUpClass(cls):
        print(f"Testing PlaylistTestCase")


    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        print(f"({self.test_url.__name__})", self.test_url.__doc__)
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEqual(view_point, resources.Playlist)


    def test_get_playlist_number_values(self):
        '''
        Checks that GET playlist return correct status code and number of values
        '''
        print(f"({self.test_get_playlist_number_values.__name__})", self.test_get_playlist_number_values.__doc__)
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEqual(resp.status_code, 200)
            data = json.loads(resp.data)
            self.assertIn('created_on', data)
            self.assertIn('_links', data)
            self.assertIn('name', data)
            self.assertIn('template', data)
            self.assertIn('author', data)
            links = data['_links']
            template_data = data['template']['data']
            self.assertEqual(len(links), self.links_number)
            self.assertEqual(len(template_data), self.template_data_number)


if __name__ == '__main__':
    print('Start running tests')
    unittest.main()