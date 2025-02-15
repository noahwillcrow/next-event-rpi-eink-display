"""
Steps to set up the Waveshare 2.13in V3 e-paper display:
1. Install the extra required dependencies by running the following command:
    - spidev
    - RPi.GPIO
    - gpiozero
2. Enable SPI on the Raspberry Pi by running the following command:
    - sudo raspi-config
    - Go to "Interfacing Options"
    - Go to "SPI"
    - Enable SPI
3. Ensure the user has the correct permissions to access the GPIO pins by running the following command:
    - sudo usermod -aG gpio <username>
4. Clone the Waveshare e-Paper repository by running the following command:
    - git clone https://github.com/waveshare/e-Paper.git
5. Replace <waveshare-path> below with the path to the cloned repository.
"""

# import sys
# sys.path.append("<waveshare-path>/RaspberryPi_JetsonNano/python/lib")

from waveshare_epd import epd2in13_V3


class Waveshare2_13InV3Renderer:
    def __init__(self):
        raise RuntimeError(
            "Please read this file and delete this error that is raised -- there is some set-up necessary to make this work."
        )
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
