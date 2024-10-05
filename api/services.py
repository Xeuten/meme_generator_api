from dataclasses import asdict

from django.db.transaction import atomic

from api.dto import MemeDTO
from api.models import Meme, MemeTemplate, User
from core.exceptions import NotFoundError


class RegisterService:
    def __init__(self, email: str, password: str):
        self._email = email
        self._password = password

    def _create_user(self) -> None:
        User.objects.create_user(email=self._email, password=self._password)

    def execute(self) -> None:
        self._create_user()


class CreateMemeService:
    def __init__(self, meme_info: MemeDTO):
        self._meme_info = meme_info

    def _check_template(self) -> MemeTemplate:
        template = MemeTemplate.objects.filter(id=self._meme_info.template_id).first()
        if not template:
            raise NotFoundError()
        return template

    def _ensure_texts(self, template: MemeTemplate) -> None:
        if not self._meme_info.top_text:
            self._meme_info.top_text = template.default_top_text
        if not self._meme_info.bottom_text:
            self._meme_info.bottom_text = template.default_bottom_text

    def _create_meme(self) -> int:
        return Meme.objects.create(**asdict(self._meme_info)).id

    def execute(self) -> int:
        with atomic():
            template = self._check_template()
            self._ensure_texts(template)
            return self._create_meme()
