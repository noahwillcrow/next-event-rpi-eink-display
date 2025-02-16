import math
import traceback
from datetime import timedelta
from PIL import Image, ImageDraw, ImageFont


class Artist:
    """This is responsible for taking a name and time-until-event pair and putting it onto the e-ink display."""

    def __init__(
        self,
        height: int,
        width: int,
        padding: int,
        path_to_font: str,
        big_text_size: int,
        small_text_size: int,
        should_flip: bool,
    ):
        self._height = height
        self._width = width
        self._padding = padding
        self._path_to_font = path_to_font
        self._big_text_size = big_text_size
        self._small_text_size = small_text_size
        self._should_flip = should_flip

    def draw_text(self, text: str) -> Image:
        """This function just draws a simple 'nothing coming up' message."""
        try:
            # create blank image
            image = Image.new('1', (self._width, self._height), 255)
            draw = ImageDraw.Draw(image)

            # define fonts
            font = ImageFont.truetype(self._path_to_font, self._big_text_size)

            # calculate text size
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_size = (text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1])

            # calculate starting y-coordinate to center the text vertically
            start_y = (self._height - text_size[1]) // 2

            # draw text
            draw.text(
                (self._padding, start_y),
                text,
                font=font,
                fill=0,
            )

            if self._should_flip == True:
                image = image.transpose(Image.ROTATE_180)

            # return the image
            return image
        except Exception as e:
            print("Error generating image:", e)
            traceback.print_exc()

    def draw_upcoming_event_notice(
        self, name: str, time_until_event: timedelta
    ) -> Image:
        """This function takes a name and a time-until-event pair and renders an e-ink compatible image."""
        try:
            # create blank image
            image = Image.new('1', (self._width, self._height), 255)
            draw = ImageDraw.Draw(image)

            # define fonts
            big_font = ImageFont.truetype(self._path_to_font, self._big_text_size)
            small_font = ImageFont.truetype(self._path_to_font, self._small_text_size)

            # calculate text sizes
            big_text = (
                f"{str(math.floor(time_until_event.total_seconds() / 60))} minutes"
            )
            small_text = f"until {name}"
            big_text_bbox = draw.textbbox((0, 0), big_text, font=big_font)
            small_text_bbox = draw.textbbox((0, 0), small_text, font=small_font)
            big_text_size = (
                big_text_bbox[2] - big_text_bbox[0],
                big_text_bbox[3] - big_text_bbox[1],
            )
            small_text_size = (
                small_text_bbox[2] - small_text_bbox[0],
                small_text_bbox[3] - small_text_bbox[1],
            )

            # calculate total text height
            total_text_height = big_text_size[1] + small_text_size[1] + self._padding

            # calculate starting y-coordinate to center the text vertically
            start_y = (self._height - total_text_height) // 2

            # draw text
            draw.text(
                (self._padding, start_y),
                big_text,
                font=big_font,
                fill=0,
            )
            draw.text(
                (self._padding, start_y + big_text_size[1] + self._padding),
                small_text,
                font=small_font,
                fill=0,
            )

            if self._should_flip == True:
                image = image.transpose(Image.ROTATE_180)

            # return the image
            return image
        except Exception as e:
            print("Error generating image:", e)
            traceback.print_exc()
