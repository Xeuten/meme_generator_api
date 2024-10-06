import random
import uuid
from dataclasses import asdict
from io import BytesIO

import requests
from django.core.files.base import ContentFile
from django.db.transaction import atomic

from api.dto import MemeDTO, RateMemeDTO
from api.models import Meme, MemeTemplate, Rating, User
from api.utils import BOTTOM_TEXTS, TOP_TEXTS, construct_meme_image
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
        """
        This method is used to update the rating if the user has already rated the
        meme, otherwise it creates a new rating. We use the update_or_create method
        provided by Django perform the operation efficiently.
        """
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


class SurpriseMeMemeService:
    def __init__(self, user_id: int):
        self._user_id = user_id
        self._top_text = random.choice(TOP_TEXTS)
        self._bottom_text = random.choice(BOTTOM_TEXTS)

    def _read_template_file(self) -> tuple[MemeTemplate, BytesIO]:
        """
        This method is used to get a random meme template from the database and read
        the image file from the URL. If the image file from the template's URL is not
        found, we iterate over the templates until we find a valid image file. If no
        valid image file is found, we raise a NotFoundError.
        """
        templates = list(MemeTemplate.objects.get_random_order_templates())
        for template in templates:
            response = requests.get(template.image_url)
            if response.status_code == 200:
                return template, BytesIO(response.content)
        raise NotFoundError()

    def _construct_meme_image(self, meme_template_io: BytesIO) -> ContentFile:
        return construct_meme_image(meme_template_io, self._top_text, self._bottom_text)

    def _create_meme(
        self, template: MemeTemplate, meme_image: ContentFile
    ) -> dict[str, str]:
        meme = Meme(
            template=template,
            created_by_id=self._user_id,
            top_text=self._top_text,
            bottom_text=self._bottom_text,
        )
        file_name = f"{template.name}_{uuid.uuid4()}.jpeg"
        meme.image.save(file_name, meme_image)
        return {"url": meme.image.url}

    def execute(self) -> dict[str, str]:
        with atomic():
            template, template_io = self._read_template_file()
            meme_image = self._construct_meme_image(template_io)
            return self._create_meme(template, meme_image)
