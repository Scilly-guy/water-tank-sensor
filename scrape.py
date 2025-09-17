#!/usr/bin/env python3
# encoding:utf-8

import RPi.GPIO as GPIO
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

TRIG = 15
ECHO = 14
PORT = 9091

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)


def measure_distance():
    """Take a single distance measurement from the HC-SR04 sensor."""
    # Ensure trigger is low
    GPIO.output(TRIG, False)
    time.sleep(0.05)

    # Send 10us pulse
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Wait for echo start
    pulse_start = time.time()
    timeout = pulse_start + 0.04
    while GPIO.input(ECHO) == 0 and time.time() < timeout:
        pulse_start = time.time()

    # Wait for echo end
    pulse_end = time.time()
    timeout = pulse_end + 0.04
    while GPIO.input(ECHO) == 1 and time.time() < timeout:
        pulse_end = time.time()

    # Calculate distance
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 2)


def average_distance(samples=10):
    """Return average of multiple sensor readings."""
    distances = []
    for _ in range(samples):
        d = measure_distance()
        if 2 <= d <= 400:  # valid range of HC-SR04
            distances.append(d)
        time.sleep(0.05)  # small delay between pings
    if distances:
        return sum(distances) / len(distances)
    else:
        return float("nan")


class PrometheusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/metrics":
            distance = average_distance(10)
            response = (
                "# HELP ultrasonic_distance_cm Average distance from ultrasonic sensor (cm)\n"
                "# TYPE ultrasonic_distance_cm gauge\n"
                f"ultrasonic_distance_cm {distance}\n"
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.end_headers()
            self.wfile.write(response.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


def run_server():
    server = HTTPServer(("", PORT), PrometheusHandler)
    print(f"Starting Prometheus exporter on port {PORT} ...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        GPIO.cleanup()


if __name__ == "__main__":
    run_server()
