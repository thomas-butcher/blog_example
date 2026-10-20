# blog/tests.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Post


class BlogTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="testuser", email="test@email.com", password="secret"
        )
        cls.post = Post.objects.create(
            title="A good title",
            body="Nice body content",
            author=cls.user,
        )

    def test_post_model(self):
        self.assertEqual(self.post.title, "A good title")
        self.assertEqual(self.post.body, "Nice body content")
        self.assertEqual(self.post.author.username, "testuser")
        self.assertEqual(str(self.post), "A good title")
        self.assertEqual(self.post.get_absolute_url(), "/post/1/")

    def test_url_exists_at_correct_location_listview(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_url_exists_at_correct_location_detailview(self):
        response = self.client.get("/post/1/")
        self.assertEqual(response.status_code, 200)

    def test_post_listview(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nice body content")
        self.assertContains(response, 'href="/post/1/"')
        self.assertTemplateUsed(response, "home.html")

    def test_post_detailview(self):
        response = self.client.get(reverse("post_detail", kwargs={"pk": self.post.pk}))
        no_response = self.client.get("/post/100000/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(no_response.status_code, 404)
        self.assertContains(response, "A good title")
        self.assertTemplateUsed(response, "post_detail.html")

    def test_static_css_linked(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "/static/css/base.css")


class AuthTests(TestCase):
    def test_signup_page(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/signup.html")

    def test_signup_creates_user_and_redirects_to_login(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "newuser",
                "password1": "a-Strong-pass-123",
                "password2": "a-Strong-pass-123",
            },
        )
        self.assertRedirects(response, reverse("login"))
        self.assertTrue(get_user_model().objects.filter(username="newuser").exists())

    def test_signup_password_mismatch(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "newuser",
                "password1": "a-Strong-pass-123",
                "password2": "different-pass-456",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(get_user_model().objects.filter(username="newuser").exists())

    def test_login_then_logout(self):
        get_user_model().objects.create_user(username="newuser", password="a-Strong-pass-123")
        response = self.client.post(
            reverse("login"), {"username": "newuser", "password": "a-Strong-pass-123"}
        )
        self.assertRedirects(response, reverse("home"))
        self.assertContains(self.client.get(reverse("home")), "Hi newuser!")

        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("home"))
        self.assertContains(self.client.get(reverse("home")), "You are not logged in.")

    def test_navbar_links(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, reverse("login"))
        self.assertContains(response, reverse("signup"))
        self.assertNotContains(response, "Log Out")

        get_user_model().objects.create_user(username="newuser", password="a-Strong-pass-123")
        self.client.login(username="newuser", password="a-Strong-pass-123")
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Log Out")
        self.assertNotContains(response, reverse("signup"))
