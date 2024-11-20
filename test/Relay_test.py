import sys

import Relay

if len(sys.argv) > 1:
    Relay.press_sensor_btn(float(sys.argv[1]))