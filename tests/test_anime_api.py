import unittest
from application import app, db
import json
import os

class TestApp(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.user = os.getenv("TEST_USER")
        self.password = os.getenv("TEST_PASS")
        self.user_id = self._login_user(self.client, self.user, self.password)

    def tearDown(self):
        pass

    def _login_user(self, client, username, password):
        response = client.post(
            "/api/v1/login",
            json={"username": username, "password": password},
            content_type="application/json",
        )
        return response.json["user_id"]

    def test_add_anime_list(self):
        # Test adding anime list
        response = self.client.post(
            "/api/v1/anime-list",
            json=[{"title": "test1", "score": 4, "user": self.user}],
            headers={"Authorization": self.user_id},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_update_anime_list(self):
        # Test add_anime_list PUT request
        response = self.client.put(
            '/api/v1/anime-list',
            json=[{"title": "test1", "score": 8, "user": self.user}],
            headers={"Authorization": self.user_id},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_add_anime_to_watchlist(self):
        # Test add_anime_to_watchlist POST request
        response = self.client.post(
            '/api/v1/watchlist',
            json=[{"anime_name": "test_anime"}],
            headers={"Authorization": self.user_id},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_remove_anime_from_watchlist(self):
        # Test add_anime_to_watchlist DELETE request
        response = self.client.delete(
            '/api/v1/watchlist',
            json=[{"anime_name": "test_anime"}],
            headers={"Authorization": self.user_id},
            content_type='application/json'
        )
        print(response)
        self.assertEqual(response.status_code, 200)

    def test_get_user_list(self):
        # Test get_user_list GET request
        response = self.client.get('/api/v1/user-list/test_user')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
