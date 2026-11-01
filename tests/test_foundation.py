import json
from html.parser import HTMLParser
from pathlib import Path
import re
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.db import IntegrityError, transaction
from django.test import Client, TestCase


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.resources = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ("src", "href") and value.startswith("/static/"):
                self.resources.append(value)


class WebsiteTests(TestCase):
    def test_public_pages_and_seo(self):
        for url, title in [
            ("/", "Une présence qui compte"),
            ("/recrutement/", "Rejoignez l’équipe"),
        ]:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, title)
            self.assertContains(response, '<html lang="fr">')
            self.assertContains(response, "noindex, nofollow")
            parser = PageParser()
            parser.feed(response.content.decode())
            from django.contrib.staticfiles import finders

            for resource in parser.resources:
                self.assertIsNotNone(finders.find(resource.removeprefix("/static/")))
            self.assertNotContains(response, "nakre-care.vercel.app")
        html = self.client.get("/").content.decode()
        data = json.loads(
            re.search(
                r'<script type="application/ld\+json">(.*?)</script>', html, re.S
            )[1]
        )
        self.assertEqual(data["telephone"], "+237674134365")
        self.assertNotIn("//static", data["logo"])

    def test_no_intake_form_or_sensitive_submission(self):
        response = self.client.get("/")
        self.assertNotContains(response, "<form")
        self.assertNotContains(response, "<input")
        self.assertNotContains(response, "contactForm")
        self.assertEqual(self.client.post("/", {"message": "FICTIF"}).status_code, 405)
        self.assertEqual(
            Client(enforce_csrf_checks=True)
            .post("/", {"message": "FICTIF"})
            .status_code,
            403,
        )
        response = self.client.get("/", {"message": "FICTIF"})
        self.assertNotContains(response, "FICTIF")
        self.assertEqual(get_user_model().objects.count(), 0)

    def test_private_routes_absent_even_for_superuser(self):
        user = get_user_model().objects.create_superuser(
            "synthetic@example.invalid", "synthetic-test-password"
        )
        for authenticated in (False, True):
            if authenticated:
                self.client.force_login(user)
            for url in [
                "/admin/",
                "/admin/login/",
                "/administration/",
                "/accounts/login/",
                "/prise-en-charge/",
                "/prise-en-charge/confirmation/",
            ]:
                self.assertEqual(self.client.get(url).status_code, 404)

    def test_recruitment_mobile_navigation_and_robots(self):
        self.assertContains(self.client.get("/recrutement/"), "data-menu-toggle")
        self.assertContains(self.client.get("/robots.txt"), "Disallow: /")
        self.assertContains(self.client.get("/sitemap.xml"), "/recrutement/</loc>")


class AccountTests(TestCase):
    def test_email_auth_and_password_hashing(self):
        user = get_user_model().objects.create_user(
            " Person@EXAMPLE.invalid ", "synthetic-test-password"
        )
        self.assertEqual(user.email, "person@example.invalid")
        self.assertNotEqual(user.password, "synthetic-test-password")
        self.assertEqual(
            authenticate(
                username="PERSON@example.invalid", password="synthetic-test-password"
            ),
            user,
        )
        user.is_active = False
        user.save()
        self.assertIsNone(
            authenticate(username=user.email, password="synthetic-test-password")
        )

    def test_database_rejects_case_insensitive_duplicates(self):
        User = get_user_model()
        User.objects.create_user("person@example.invalid")
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.bulk_create([User(email="PERSON@example.invalid")])

    def test_no_password_means_unusable(self):
        user = get_user_model().objects.create_user("person@example.invalid")
        self.assertFalse(user.has_usable_password())
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_invalid_user_creation(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(" ")
        with self.assertRaises(ValueError):
            get_user_model().objects.create_superuser(
                "person@example.invalid", is_staff=False
            )


class ProductionConfigurationTests(TestCase):
    def test_missing_secrets_or_broad_hosts_fail_closed(self):
        import os
        import secrets
        import subprocess
        import sys

        base = {
            k: v
            for k, v in os.environ.items()
            if k
            not in (
                "DJANGO_SECRET_KEY",
                "DATABASE_URL",
                "DJANGO_ALLOWED_HOSTS",
                "PUBLIC_ORIGIN",
            )
        }
        base["DJANGO_SETTINGS_MODULE"] = "config.settings.production"
        for overrides in (
            {},
            {
                "DJANGO_SECRET_KEY": secrets.token_urlsafe(64),
                "DJANGO_ALLOWED_HOSTS": "*",
            },
        ):
            with self.subTest(overrides=list(overrides)):
                result = subprocess.run(
                    [sys.executable, "-c", "import django; django.setup()"],
                    env={**base, **overrides},
                    capture_output=True,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(b"ImproperlyConfigured", result.stderr)
