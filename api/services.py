from dataclasses import asdict

from django.db.transaction import atomic

from api.dto import MemeDTO, RateMemeDTO
from api.models import Meme, MemeTemplate, Rating, User


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
        return MemeTemplate.objects.get_template_or_404(self._meme_info.template_id)

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


class MemeService:
    def __init__(self, meme_id: int):
        self._meme_id = meme_id

    def _get_meme(self) -> Meme:
        return Meme.objects.get_meme_or_404(meme_id=self._meme_id, perform_joins=True)

    def execute(self) -> Meme:
        return self._get_meme()


class RateMemeService:
    def __init__(self, rate_meme_info: RateMemeDTO):
        self._rate_meme_info = rate_meme_info

    def _check_meme(self) -> None:
        Meme.objects.get_meme_or_404(meme_id=self._rate_meme_info.meme_id)

    def _update_or_create_rating(self) -> int:
        rating, _ = Rating.objects.update_or_create(
            meme_id=self._rate_meme_info.meme_id,
            user_id=self._rate_meme_info.user_id,
            defaults={"score": self._rate_meme_info.score},
        )
        return rating.id

    def execute(self) -> int:
        with atomic():
            self._check_meme()
            return self._update_or_create_rating()
