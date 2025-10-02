#
#
#
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, HourLocator
from datetime import datetime
from pathlib import Path

from MonitoringBase import *

#######################################################################
class Monitoring( MonitoringBase):
    def __init__(self, COUNT_DATE):
        super().__init__( COUNT_DATE)

    def plot_warning( self, ss_type, dfy, ax, cfg):
        mrad2deg = 0.0573  
        if ss_type=='RAIN':
            upper = np.array( [cfg.normal, cfg.alert, cfg.alarm] )
            lower = upper 
        elif ss_type=='TILT':
            thres = mrad2deg*np.array( [cfg.normal, cfg.alert, cfg.alarm] )
            upper = dfy.mean() + thres
            lower = dfy.mean() - thres
        elif ss_type=='ODS':
            thres = np.array( [cfg.normal, cfg.alert, cfg.alarm] )/1000
            upper = dfy.mean() + thres
            lower = dfy.mean() - thres
        COLORS = ['green', 'orange', 'red'] 
        for uplo in [upper,lower]:
            for level, color  in zip(uplo, COLORS): 
                ax.axhline( y=level, color=color,  linestyle=(0, (10, 5)), linewidth=1)

    def plot_daily_data( self, args, ax ):
        daily, ss_type, title, dfx, dfy = args
        cfg = self.CONFIG[ss_type]
        #import pdb ;pdb.set_trace()
        if len(dfx)>0:
            ax.plot( dfx, dfy, lw=cfg.linewidth,
            color=cfg.color,           # your configured color
            marker="o",                # small circle markers
            markersize = cfg.markersize, alpha=0.6 )
            self.plot_warning( ss_type, dfy, ax, cfg)
        ax.set_title(title, loc="left")
        #ax.set_ylabel( dfy )
        ax.grid(True, alpha=0.3)
        #########################################################
        day0 = pd.to_datetime( daily )
        start = day0
        end = day0 + pd.Timedelta(days=1)
        ax.set_xlim(start, end)
        ax.xaxis.set_major_locator(HourLocator(byhour=range(0, 25, 2)))
        ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
        ax.set_xlabel("Time (HH:MM)")

    ###########################################################################
    def DoSaveFig( self, fig, DAILY ):
        dt = datetime.strptime(DAILY, "%Y-%m-%d")
        DT = dt.strftime("%Y-%m-%d").replace("-", "")
        outdir = Path("./CACHE") / DT
        outdir.mkdir(parents=True, exist_ok=True)

        PNG = outdir / f"{DT}_all.png"
        print( f'Writing to {PNG}...')
        fig.savefig( PNG, dpi=600)

        SVG = outdir / f"{DT}_all.svg"
        print( f'Writing to {SVG}...')
        fig.savefig( SVG, dpi=600)

        PDF = outdir / f"{DT}_all.pdf"
        print( f'Writing to {PDF}...')
        fig.savefig( PDF, dpi=600)
