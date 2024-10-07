import random
import uuid
from dataclasses import asdict
from io import BytesIO

import requests
from django.core.files.base import ContentFile
from django.db.transaction import atomic
from PIL import Image, ImageDraw, ImageFont

from api.consts import BOTTOM_TEXTS, TOP_TEXTS
from api.dto import MemeDTO, RateMemeDTO
from api.models import Meme, MemeTemplate, Rating
from core.exceptions import NotFoundError


class CreateMemeService:
    def __init__(self, meme_data: MemeDTO):
        self._meme_data = meme_data

    def _get_full_meme_data(self) -> MemeDTO:
        template = MemeTemplate.objects.get_template_or_404(self._meme_data.template_id)
        top_text = (
            self._meme_data.top_text
            if self._meme_data.top_text
            else template.default_top_text
        )
        bottom_text = (
            self._meme_data.bottom_text
            if self._meme_data.bottom_text
            else template.default_bottom_text
        )
        return MemeDTO(
            template_id=template.id,
            created_by_id=self._meme_data.created_by_id,
            top_text=top_text,
            bottom_text=bottom_text,
        )

    def _create_meme(self, full_meme_info: MemeDTO) -> int:
        return Meme.objects.create(**asdict(full_meme_info)).id

    def execute(self) -> int:
        with atomic():
            full_meme_info = self._get_full_meme_data()
            return self._create_meme(full_meme_info)


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

    def _get_width_height(
        self, text: str, draw: ImageDraw, font: ImageFont
    ) -> tuple[int, int]:
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        return abs(right - left), abs(bottom - top)

    def _construct_meme_image(self, meme_template_io: BytesIO) -> ContentFile:
        img = Image.open(meme_template_io)
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()

        text_width, text_height = self._get_width_height(self._top_text, draw, font)
        top_position = ((img.width - text_width) / 2, 0)
        draw.text(
            top_position,
            self._top_text,
            fill="white",
            font=font,
            stroke_width=2,
            stroke_fill="black",
        )

        text_width, text_height = self._get_width_height(self._bottom_text, draw, font)
        bottom_position = ((img.width - text_width) / 2, img.height - text_height)
        draw.text(
            bottom_position,
            self._bottom_text,
            fill="white",
            font=font,
            stroke_width=2,
            stroke_fill="black",
        )

        meme_img_io = BytesIO()
        img.save(meme_img_io, format="JPEG")
        return ContentFile(meme_img_io.getvalue())

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
