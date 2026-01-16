from bme280 import BME280
import time

sensor = BME280()

while True:
    temp, pressure, humidity = sensor.read()
    print(f"Temp: {temp:.2f} °C")
    print(f"Pressure: {pressure:.2f} hPa")
    print(f"Humidity: {humidity:.2f} %")
    print("-" * 20)
    time.sleep(2)
