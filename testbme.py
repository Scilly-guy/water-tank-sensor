import board
import adafruit_bme280 as bme280
import time

i2c = board.I2C()  # uses /dev/i2c-1
bme280 = bme280.Adafruit_BME280_I2C(i2c)

bme280.sea_level_pressure = 1013.25  # adjust for your location

while True:
    print(f"Temp: {bme280.temperature:.1f} °C")
    print(f"Humidity: {bme280.humidity:.1f} %")
    print(f"Pressure: {bme280.pressure:.1f} hPa")
    print("-" * 20)
    time.sleep(2)