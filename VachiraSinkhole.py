#
# ReadVachira
#
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
from Monitoring import *

##################################################################
##################################################################
##################################################################
import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Plot SenCeive CSV by sensors and accummulated rainfall")
    parser.add_argument( "-d", "--date_time",type=str, default=None,
        help="วันเวลาในรูปแบบ YYYY-MM-DD")
    parser.add_argument("-p", "--popup", action="store_true",
                        help="Show the plot in a popup window.")
    args = parser.parse_args()

    moni = Monitoring( args )
    if args.date_time:
        moni.PlotDaily( args.date_time )
    print("=============== Finish ============" )


