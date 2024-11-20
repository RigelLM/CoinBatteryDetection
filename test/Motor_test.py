import sys

import Scan

if len(sys.argv) > 1:
    if sys.argv[2] == "CCW":
        Scan.stepper_move(int(sys.argv[1]), Scan.CCW)
    else:
        Scan.stepper_move(int(sys.argv[1]), Scan.CW)