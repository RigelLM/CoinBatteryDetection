import sys

import Scan

if len(sys.argv) > 1:
    print(Scan.get_median_dis(int(sys.argv[1])))