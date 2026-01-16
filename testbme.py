from Adafruit_BME280 import *

sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)

degrees = sensor.read_temperature()
pascals = sensor.read_pressure()
hectopascals = pascals / 100
humidity = sensor.read_humidity()

print(f'Temp      = {degrees:0.2f} deg C')
print(f'Pressure  = {hectopascals:0.2f} hPa')
print(f'Humidity  = {humidity:0.2f} %')