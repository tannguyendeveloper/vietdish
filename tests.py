from unittest import TestCase
from app import app

class AppTestApp(TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_home_page(self):
        """ Test the initial page load of the application """
        with self.client:
            res =self.client.get('/')
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn('<p>Aggregated Vietnamese and Asian-Fusion Recipes.</p>', html)

    def test_search_page(self):
        """ Test the initial page load of the application """
        with self.client:
            res =self.client.get('/search/')
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn('<p>Aggregated Vietnamese and Asian-Fusion Recipes.</p>', html)

    def test_recipe_page(self):
        """ Test printable recipe page """
        with self.client:
            res =self.client.get('/recipes/21665')
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn('<div id="recipe" class="recipe-container">', html)

    def test_recipe_printable_page(self):
        """ Test printable recipe page """
        with self.client:
            res =self.client.get('/recipes/867475/print')
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn('<h2>Ingredients</h2>', html)

    def test_api_favorite_user_not_logged_in(self):
        """ Test the favorite api """
        with self.client:
            res = self.client.post('/api/favorites/')
            self.assertEqual(res.status_code, 400)

    def test_api_review_user_not_logged_in(self):
        """ Test the review api """
        with self.client:
            res = self.client.post('/api/reviews/')
            self.assertEqual(res.status_code, 400)
