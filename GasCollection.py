import st7735
from bme280 import BME280
from enviroplus import gas
import logging

try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559


class GasCollection:
    def __init__(self) -> None:
        self.bme280 = BME280()
        self.cpu_temps = [self.get_cpu_temperature()] * 5
        self.factor = 2.25

    def get_cpu_temperature(self):
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = f.read()
            temp = int(temp) / 1000.0
        return temp 
    

    def getData(self):

        cpu_temp = self.get_cpu_temperature()
        cpu_temps = self.cpu_temps[1:] + [cpu_temp]
        avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
        raw_temp = self.bme280.get_temperature()
        Temperaturedata = raw_temp - ((avg_cpu_temp - raw_temp) / self.factor)


        unit = "hPa"
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

        hazardous_gas_data = {'reducing' : Convertedreduced, 'oxidising' : Convertedoxidised ,
                              'ammonia' : ConvertedNh3, 
                            'pressure' : Pressuredata, 'temperature' : Temperaturedata,
                            'humidity' : Humiditydata, 'light' : Lightdata
                              }
        # self.displayLCD(hazardous_gas_data)
        return hazardous_gas_data
    

    # def displayLCD(self, gas_data):

        # print(hazardous_gas_data)    
        # print(Temperaturedata)
        # print(Pressuredata)
        # print(Humiditydata)
        # print(Lightdata)
        # print(Convertedreduced)
        # print(Convertedoxidised)
        # print(ConvertedNh3)




# gc = GasCollection()

# print(gc.getData())


