import st7735
from bme280 import BME280
from enviroplus import gas
import logging
from fonts.ttf import RobotoMedium as UserFont
from PIL import Image, ImageDraw, ImageFont
import socket
import time
import colorsys
import cv2
import numpy as np
try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559


class GasCollection:
    def __init__(self) -> None:


        ### Gas Sensors ###
        self.bme280 = BME280()
        self.cpu_temps = [self.get_cpu_temperature()] * 5
        self.factor = 2.25

        ### LCD ###
        self.st7735 = st7735.ST7735(
        port=0,
        cs=1,
        dc="GPIO9",
        backlight="GPIO12",
        rotation=270,
        spi_speed_hz=10000000
        )
        self.st7735.begin()         # Initialize display
        self.WIDTH = self.st7735.width
        self.HEIGHT = self.st7735.height
        self.top_pos = 25

        # Set up canvas and font
        self.img = Image.new("RGB", (self.WIDTH, self.HEIGHT), color=(0, 0, 0))
        self.draw = ImageDraw.Draw(self.img)
        font_size = 20
        self.font = ImageFont.truetype(UserFont, font_size)
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.ip = s.getsockname()[0]
        s.close()

        ### Proximity ###
        self.mode = 0
        self.delay = 0.5
        self.last_page = 0
        

        self.values = {}
        self.variables = [
            "ip", # 0
            "temperature", # 1
            "pressure", # 2 
            "humidity", # 3
            "light", # 4
            "oxidised", # 5
            "reduced", # 6
            "nh3", # 7
            "feeed", #8
             ]
        
        for v in self.variables:
            self.values[v] = [1] * self.WIDTH

    def display_text(self, variable, data, unit):
        # Maintain length of list
        self.values[variable] = self.values[variable][1:] + [data]
        # Scale the values for the variable between 0 and 1
        vmin = min(self.values[variable])
        vmax = max(self.values[variable])
        colours = [(v - vmin + 1) / (vmax - vmin + 1) for v in self.values[variable]]
        # Format the variable name and value
        message = f"{variable[:4]}: {data:.1f} {unit}"
        logging.info(message)
        self.draw.rectangle((0, 0, self.WIDTH, self.HEIGHT), (255, 255, 255))
        for i in range(len(colours)):
            # Convert the values to colours from red to blue
            colour = (1.0 - colours[i]) * 0.6
            r, g, b = [int(x * 255.0) for x in colorsys.hsv_to_rgb(colour, 1.0, 1.0)]
            # Draw a 1-pixel wide rectangle of colour
            self.draw.rectangle((i, self.top_pos, i + 1, self.HEIGHT), (r, g, b))
            # Draw a line graph in black
            line_y = self.HEIGHT - (self.top_pos + (colours[i] * (self.HEIGHT - self.top_pos))) + self.top_pos
            self.draw.rectangle((i, line_y, i + 1, line_y + 1), (0, 0, 0))
        # Write the text at the top in black
        self.draw.text((0, 0), message, font = self.font, fill=(0, 0, 0))
        self.st7735.display(self.img)
    def __del__(self):
        self.st7735.reset()

    def get_cpu_temperature(self):
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = f.read()
            temp = int(temp) / 1000.0
        return temp 
    
    def display_ip(self):        
        self.draw.rectangle((0, 0, self.WIDTH, self.HEIGHT), (255, 255, 255))
        self.draw.text((0, 0), self.ip, font=self.font, fill=(0, 0, 0))
        self.st7735.display(self.img)

    def getData(self):

        cpu_temp = self.get_cpu_temperature()
        cpu_temps = self.cpu_temps[1:] + [cpu_temp]
        avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
        raw_temp = self.bme280.get_temperature()
        Temperaturedata = raw_temp - ((avg_cpu_temp - raw_temp) / self.factor)


        Pressuredata = self.bme280.get_pressure()
        Humiditydata = self.bme280.get_humidity()
        Lightdata = ltr559.get_lux()
        data = gas.read_all()
        RsOxidised = data.oxidising / 1000
        Oxidisedratio = RsOxidised / 321.9
        Convertedoxidised = (-24.435 * Oxidisedratio) + 146.06
        if Convertedoxidised < 0:
            Convertedoxidised = 0

        # Collect reduced gas data
        RsReduced = data.reducing / 1000
        Reducedratio = RsReduced / 11.2
        Convertedreduced = (0.1561 * Reducedratio) + 0.0002
        if Convertedreduced < 0:
            Convertedreduced = 0

        Rsnh3 = data.nh3 / 1000
        Nh3ratio = Rsnh3 / 225.3
        ConvertedNh3 = (-55.586 * Nh3ratio) + 83.139
        if ConvertedNh3 < 0:
            ConvertedNh3 = 0

        hazardous_gas_data = {'reducing' : round(Convertedreduced,3), 'oxidising' : round(Convertedoxidised,3) ,
                              'ammonia' : round(ConvertedNh3,3), "time" : 0,
                            'pressure' : round(Pressuredata,3), 'temperature' : round(Temperaturedata,3),
                            'humidity' : round(Humiditydata,3), 'light' : round(Lightdata,3)
                              }
        # self.displayLCD(hazardous_gas_data)
        return hazardous_gas_data


    def pollProximity(self):
        proximity = ltr559.get_proximity()
        if proximity > 1500 and time.time() - self.last_page > self.delay:
            self.mode += 1
            self.mode %= len(self.variables)
            print(self.mode)
            self.last_page = time.time()

    def updateLCD(self, gasData, frame):
        self.pollProximity()
        if self.mode == 0:
            self.display_ip()
        elif self.mode == 1:
            # variable = "temperature"
            unit = "°C"
            self.display_text(self.variables[self.mode], gasData["temperature"], unit)
        elif self.mode == 2:
            # variable = "pressure"
            unit = "hPa"
            self.display_text(self.variables[self.mode], gasData["pressure"], unit)

        elif self.mode == 3:
            # variable = "humidity"
            unit = "%"
            self.display_text(self.variables[self.mode], gasData["humidity"], unit)
        elif self.mode == 4:
            # variable = "light"
            unit = "Lux"
            self.display_text(self.variables[self.mode], gasData["light"], unit)
        elif self.mode == 5:
            # variable = "oxidising"
            unit = "ppm"
            self.display_text(self.variables[self.mode], gasData["oxidising"], unit)
        elif self.mode == 6:
            # variable = "reducing"
            unit = "ppm"
            self.display_text(self.variables[self.mode], gasData["reducing"], unit)
        elif self.mode == 7:
            # variable = "ammonia"
            unit = "ppm"
            self.display_text(self.variables[self.mode], gasData["ammonia"], unit)
        elif self.mode == 8:
            resizedFrame = cv2.resize(frame, (self.HEIGHT,self.WIDTH), interpolation=cv2.INTER_CUBIC)
            self.st7735.display(Image.fromarray(resizedFrame).convert('RGB'))




# gc = GasCollection()

# while(1):
#     data = gc.getData()
#     gc.updateLCD(data)


