from api.models import User


class RegisterService:
    def __init__(self, email: str, password: str):
        self._email = email
        self._password = password

    def _create_user(self) -> None:
        User.objects.create_user(email=self._email, password=self._password)

    def execute(self) -> None:
        self._create_user()
