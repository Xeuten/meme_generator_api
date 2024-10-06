from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

TOP_TEXTS = [
    "When you finally finish your work…",
    "Me trying to explain why…",
    "When you see your friends making plans without you…",
    "That feeling when you’re about to relax…",
    "Me walking into the room like…",
    "When you're about to say something smart…",
    "When you know the answer but the teacher calls on someone else…",
    "Me when I realize I forgot something important…",
    "When you're trying to be productive but…",
    "That moment when you think everything is going well…",
]


BOTTOM_TEXTS = [
    "…and your boss gives you another task.",
    "…but no one is listening.",
    "…but you weren't invited.",
    "…and your phone rings.",
    "…like I own the place.",
    "…and you mess it up completely.",
    "…and they say the exact thing you were about to say.",
    "…and it's already too late.",
    "…but end up binge-watching Netflix instead.",
    "…and then everything goes horribly wrong.",
]


def get_width_height(text: str, draw: ImageDraw, font: ImageFont) -> tuple[int, int]:
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return abs(right - left), abs(bottom - top)


def construct_meme_image(io: BytesIO, top_text: str, bottom_text: str) -> ContentFile:
    img = Image.open(io)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    text_width, text_height = get_width_height(top_text, draw, font)
    top_position = ((img.width - text_width) / 2, 0)
    draw.text(
        top_position,
        top_text,
        fill="white",
        font=font,
        stroke_width=2,
        stroke_fill="black",
    )

    text_width, text_height = get_width_height(bottom_text, draw, font)
    bottom_position = ((img.width - text_width) / 2, img.height - text_height)
    draw.text(
        bottom_position,
        bottom_text,
        fill="white",
        font=font,
        stroke_width=2,
        stroke_fill="black",
    )

    meme_img_io = BytesIO()
    img.save(meme_img_io, format="JPEG")
    return ContentFile(meme_img_io.getvalue())
