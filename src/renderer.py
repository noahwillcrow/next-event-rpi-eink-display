import os
from PIL import Image
from typing import Dict, Callable

renderers_by_name: Dict[str, Callable[[Image.Image], None]] = {}


def render_to_waveshare_2_13_in_v3(image: Image):
    from renderers.waveshare_2_13_in_v3_renderer import Waveshare2_13InV3Renderer

    renderer = Waveshare2_13InV3Renderer()
    renderer.render(image)


renderers_by_name['waveshare-2.13in-v3'] = render_to_waveshare_2_13_in_v3


def render_to_file(image: Image):
    image.save(os.path.join(os.path.dirname(__file__), './output.png'))


renderers_by_name['to-file'] = render_to_file


class Renderer:
    """This is responsible for simply rendering an image to the appropriate display given a string name of the display type."""

    def __init__(self, renderer_name: str):
        self._render_func = renderers_by_name[renderer_name]

    def render(self, image: Image):
        self._render_func(image)
