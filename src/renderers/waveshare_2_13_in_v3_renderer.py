from waveshare_epd import epd2in13_V3


class Waveshare2_13InV3Renderer:
    def __init__(self):
        self.epd = epd2in13_V3.EPD()
        self.epd.init()
        self.epd.Clear()
        self.width = self.epd.width
        self.height = self.epd.height

    def render(self, image):
        self.epd.display(self.epd.getbuffer(image))

    def clear(self):
        self.epd.Clear()

    def __del__(self):
        self.epd.sleep()
        self.epd.Dev_exit()
