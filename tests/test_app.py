import unittest
from app import create_app, db

class ProfileForgeTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", "SECRET_KEY": "test-secret"})
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_home_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"ProfileForge", response.data)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "ok")

    def test_profile_can_be_updated(self):
        response = self.client.post("/profile", data={
            "full_name":"Taylor Example","headline":"Platform Engineer","bio":"I build useful things.",
            "email":"taylor@example.com","location":"Lahore","skills":"Docker, Kubernetes",
            "github":"https://github.com/example","linkedin":"https://linkedin.com/in/example","website":"https://example.com"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Taylor Example", response.data)

    def test_project_can_be_added(self):
        response = self.client.post("/projects", data={"title":"Test Project","description":"A project for testing.","technologies":"Flask, pytest","project_url":"https://github.com/"}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test Project", response.data)

    def test_project_requires_title_and_description(self):
        response = self.client.post("/projects", data={"title":"","description":""}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"required", response.data.lower())

if __name__ == "__main__":
    unittest.main()
