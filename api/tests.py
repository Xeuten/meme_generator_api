from django.test import TestCase
from rest_framework import status
from rest_framework.response import Response

from api.models import Meme


class MemeGeneratorApiTest(TestCase):
    fixtures = ["fixtures/initial_test_data.json"]

    def _assertResponseIsOk(self, response: Response) -> None:
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def _assertResponseIsCreated(self, response: Response) -> None:
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def _assertResponseIsBadRequest(self, response: Response) -> None:
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _assertResponseIsUnauthorized(self, response: Response) -> None:
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _assertResponseIsNotFound(self, response: Response) -> None:
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def _authenticate(
        self,
        *,
        register: bool = True,
        email: str = "test@gmail.com",
        password: str = "test",
    ) -> str:
        if register:
            self._register_user(email=email, password=password)
        response = self.client.post(
            path="/api/token/",
            data={"email": email, "password": password},
        )
        json = response.json()
        access = json["access"]
        refresh = json["refresh"]
        self.client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {access}"
        return refresh

    def _register_user(
        self, email: str = "test@gmail.com", password: str = "test"
    ) -> Response:
        return self.client.post(
            path="/api/register/",
            data={"email": email, "password_1": password, "password_2": password},
        )

    def test_register_success(self):
        self._assertResponseIsCreated(self._register_user())

    def test_register_failure_user_exists(self):
        self._register_user()
        self._assertResponseIsBadRequest(self._register_user())

    def test_register_failure_passwords_do_not_match(self):
        self._assertResponseIsBadRequest(
            self.client.post(
                path="/api/register/",
                data={
                    "email": "test@gmail.com",
                    "password_1": "test",
                    "password_2": "te",
                },
            )
        )

    def test_authentication_success(self):
        self._register_user()
        self._assertResponseIsOk(
            self.client.post(
                path="/api/token/",
                data={"email": "test@gmail.com", "password": "test"},
            )
        )

    def test_authentication_failure_wrong_password(self):
        self._register_user()
        self._assertResponseIsUnauthorized(
            self.client.post(
                path="/api/token/",
                data={"email": "test@gmail.com", "password": "wrong"},
            )
        )

    def test_refresh_token_success(self):
        refresh = self._authenticate()
        self._assertResponseIsOk(
            self.client.post(
                path="/api/token/refresh/",
                data={"refresh": refresh},
            )
        )

    def test_refresh_token_failure_wrong_refresh(self):
        self._assertResponseIsUnauthorized(
            self.client.post(
                path="/api/token/refresh/",
                data={"refresh": "wrong"},
            )
        )

    def test_list_templates_success(self):
        self._authenticate()
        self._assertResponseIsOk(self.client.get(path="/api/templates/"))

    def test_list_templates_failure_unauthenticated(self):
        self._assertResponseIsUnauthorized(self.client.get(path="/api/templates/"))

    def test_list_memes_success(self):
        self._authenticate()
        self._assertResponseIsOk(self.client.get(path="/api/memes/"))

    def test_list_memes_failure_non_existent_page(self):
        self._authenticate()
        self._assertResponseIsNotFound(self.client.get(path="/api/memes/?page=10"))

    def test_create_meme_success(self):
        self._authenticate()
        self._assertResponseIsCreated(
            self.client.post(
                path="/api/memes/",
                data={"template_id": 1, "top_text": "Top", "bottom_text": "Bottom"},
            )
        )

    def test_create_meme_failure_non_existent_template(self):
        self._authenticate()
        self._assertResponseIsNotFound(
            self.client.post(
                path="/api/memes/",
                data={"template_id": 100, "top_text": "Top", "bottom_text": "Bottom"},
            )
        )

    def test_retrieve_meme_success(self):
        self._authenticate()
        self._assertResponseIsOk(self.client.get(path="/api/memes/1/"))

    def test_retrieve_meme_failure_non_existent_meme(self):
        self._authenticate()
        self._assertResponseIsNotFound(self.client.get(path="/api/memes/100/"))

    def test_rate_meme_success(self):
        self._authenticate()
        self._assertResponseIsCreated(
            self.client.post(path="/api/memes/1/rate/", data={"score": 5})
        )

    def test_rate_meme_failure_incorrect_score(self):
        self._authenticate()
        self._assertResponseIsBadRequest(
            self.client.post(path="/api/memes/1/rate/", data={"score": 6})
        )

    def test_rate_meme_failure_non_existent_meme(self):
        self._authenticate()
        self._assertResponseIsNotFound(
            self.client.post(path="/api/memes/100/rate/", data={"score": 5})
        )

    def test_random_meme_success(self):
        self._authenticate()
        self._assertResponseIsOk(self.client.get(path="/api/memes/random/"))

    def test_random_meme_failure_no_memes(self):
        Meme.objects.all().delete()
        self._authenticate()
        self._assertResponseIsNotFound(self.client.get(path="/api/memes/random/"))

    def test_top_memes_success(self):
        self._authenticate()
        self._assertResponseIsOk(self.client.get(path="/api/memes/top/"))

    def test_surprise_me_success(self):
        self._authenticate()
        self._assertResponseIsOk(self.client.get(path="/api/memes/surprise-me/"))
