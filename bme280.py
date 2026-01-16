import smbus
import time

# BME280 default address
BME280_I2C_ADDR = 0x76

# Registers
REG_ID = 0xD0
REG_RESET = 0xE0
REG_CTRL_HUM = 0xF2
REG_STATUS = 0xF3
REG_CTRL_MEAS = 0xF4
REG_CONFIG = 0xF5
REG_PRESS_MSB = 0xF7

class BME280:
    def __init__(self, bus=1, address=BME280_I2C_ADDR):
        self.bus = smbus.SMBus(bus)
        self.address = address
        self._load_calibration()
        self._configure()

    def _read_u8(self, reg):
        return self.bus.read_byte_data(self.address, reg)

    def _read_s8(self, reg):
        val = self._read_u8(reg)
        return val - 256 if val > 127 else val

    def _read_u16(self, reg):
        lsb = self._read_u8(reg)
        msb = self._read_u8(reg + 1)
        return (msb << 8) | lsb

    def _read_s16(self, reg):
        result = self._read_u16(reg)
        return result - 65536 if result > 32767 else result

    def _load_calibration(self):
        # Temperature calibration
        self.dig_T1 = self._read_u16(0x88)
        self.dig_T2 = self._read_s16(0x8A)
        self.dig_T3 = self._read_s16(0x8C)

        # Pressure calibration
        self.dig_P1 = self._read_u16(0x8E)
        self.dig_P2 = self._read_s16(0x90)
        self.dig_P3 = self._read_s16(0x92)
        self.dig_P4 = self._read_s16(0x94)
        self.dig_P5 = self._read_s16(0x96)
        self.dig_P6 = self._read_s16(0x98)
        self.dig_P7 = self._read_s16(0x9A)
        self.dig_P8 = self._read_s16(0x9C)
        self.dig_P9 = self._read_s16(0x9E)

        # Humidity calibration
        self.dig_H1 = self._read_u8(0xA1)
        self.dig_H2 = self._read_s16(0xE1)
        self.dig_H3 = self._read_u8(0xE3)

        e4 = self._read_s8(0xE4)
        e5 = self._read_u8(0xE5)
        e6 = self._read_s8(0xE6)

        self.dig_H4 = (e4 << 4) | (e5 & 0x0F)
        self.dig_H5 = (e6 << 4) | (e5 >> 4)
        self.dig_H6 = self._read_s8(0xE7)

    def _configure(self):
        # Humidity oversampling x1
        self.bus.write_byte_data(self.address, REG_CTRL_HUM, 0x01)
        # Temp & pressure oversampling x1, normal mode
        self.bus.write_byte_data(self.address, REG_CTRL_MEAS, 0x27)
        # Standby 1000ms, filter off
        self.bus.write_byte_data(self.address, REG_CONFIG, 0xA0)

    def _read_raw_data(self):
        data = self.bus.read_i2c_block_data(self.address, REG_PRESS_MSB, 8)

        adc_p = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        adc_t = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        adc_h = (data[6] << 8) | data[7]

        return adc_t, adc_p, adc_h

    def read(self):
        adc_t, adc_p, adc_h = self._read_raw_data()

        # Temperature compensation
        var1 = (adc_t / 16384.0 - self.dig_T1 / 1024.0) * self.dig_T2
        var2 = ((adc_t / 131072.0 - self.dig_T1 / 8192.0) ** 2) * self.dig_T3
        t_fine = var1 + var2
        temperature = t_fine / 5120.0

        # Pressure compensation
        var1 = t_fine / 2.0 - 64000.0
        var2 = var1 * var1 * self.dig_P6 / 32768.0
        var2 += var1 * self.dig_P5 * 2.0
        var2 = var2 / 4.0 + self.dig_P4 * 65536.0
        var1 = (self.dig_P3 * var1 * var1 / 524288.0 + self.dig_P2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * self.dig_P1

        if var1 == 0:
            pressure = 0
        else:
            pressure = 1048576.0 - adc_p
            pressure = (pressure - var2 / 4096.0) * 6250.0 / var1
            var1 = self.dig_P9 * pressure * pressure / 2147483648.0
            var2 = pressure * self.dig_P8 / 32768.0
            pressure += (var1 + var2 + self.dig_P7) / 16.0

        # Humidity compensation
        h = t_fine - 76800.0
        humidity = (adc_h - (self.dig_H4 * 64.0 + self.dig_H5 / 16384.0 * h)) * (
            self.dig_H2 / 65536.0 * (1.0 + self.dig_H6 / 67108864.0 * h *
            (1.0 + self.dig_H3 / 67108864.0 * h))
        )
        humidity *= (1.0 - self.dig_H1 * humidity / 524288.0)
        humidity = max(0.0, min(100.0, humidity))

        return temperature, pressure / 100.0, humidity
