#
# ReadVachira
#
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
import tomllib

class MonitoringBase:
    def __init__(self, args):
        with open("CONFIG.toml", "rb") as f:
            config = tomllib.load(f)
        self.ARGS = args
        self.CONFIG = {section: pd.Series(params) for section, params in config.items()}
        #import pdb ;pdb.set_trace()
        self.ReadRainFall()
        self.ReadSensor( )

    def ReadRainFall(self):
        PATH_RAIN = Path( './DataRain/*.csv' )
        files = list(PATH_RAIN.parent.glob(PATH_RAIN.name))
        valid_files = [f for f in files if os.path.isfile(f)]
        if not valid_files:
            print( f'*** ERROR *** Expecting rainfall data in "{PATH_RAIN}"...')
            raise FileNotFoundError("No valid rainfall CSV files found in given list")

        df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
        def buddhist_to_gregorian(date_str):
            d, t = date_str.split(" ")
            day, month, year = map(int, d.split("/"))
            year -= 543   # พ.ศ. → ค.ศ.
            return f"{day:02d}/{month:02d}/{year:04d} {t}"
        df["datetime"] = pd.to_datetime( df["วัน-เวลา"].map(buddhist_to_gregorian),
                                 format="%d/%m/%Y %H:%M")
        print(df.head())

        dups = df.duplicated(subset=["รหัสสถานี", "วัน-เวลา"], keep=False)
        print("จำนวน duplicates:", dups.sum())
        print(df[dups].sort_values(["รหัสสถานี", "วัน-เวลา"]))
        df_clean = df.drop_duplicates(subset=["รหัสสถานี", "วัน-เวลา"], 
                                      keep="first").reset_index(drop=True)
        print("ขนาด DataFrame หลังลบ duplicates:", df_clean.shape)
        df_clean.sort_values(by="datetime", inplace=True)
        df_clean = df_clean.reset_index(drop=True)
        
        df_clean["date"] = df_clean["datetime"].dt.date
        daily_counts = df_clean.groupby("date").size().reset_index(name="count")
        print(daily_counts)
        #import pdb ;pdb.set_trace()
        self.dfRAIN = df_clean

    def ReadSensor(self):
        PATH_SENSOR = Path( './/DataSensor/*.csv' )
        files = list(PATH_SENSOR.parent.glob(PATH_SENSOR.name))
        valid_files = [f for f in files if os.path.isfile(f)]
        if not valid_files:
            print( f'*** ERROR *** Expecting SC sensor data in "{PATH_SENSOR}"...')
            raise FileNotFoundError("No valid rainfall CSV files found in given list")
        dfs = list()
        for fi in files:
            df = pd.read_csv( fi , index_col=False, encoding="latin1" )
            df["Units"] = ( df["Units"].replace({
                "ýý": "m",    # 
                "ýýc": "°C",   # degrees Celsius (temperature)
            }))
            dfs.append( df )
        df = pd.concat( dfs, ignore_index=True)

        df["Sample Time"] = pd.to_datetime(df["Sample Time"])
        #df["BKK_dt"] = df["Sample Time"].dt.tz_localize("Asia/Bangkok")
        df["datetime"] = df["Sample Time"]   # already BKK time
        df["date"] = df["datetime"].dt.date
        #import pdb ;pdb.set_trace()

        counts = df["date"].value_counts().sort_index()
        print(counts)
        self.dfSENSOR = df

    def PlotDaily( self, DAILY ):
        dfRAIN = self.dfRAIN[self.dfRAIN["date"]==pd.to_datetime(DAILY).date()]
        df = self.dfSENSOR[self.dfSENSOR["date"]==pd.to_datetime(DAILY).date()]
        #import pdb ;pdb.set_trace()
        df_tilt = df[df["Sensor Type"].isin([
            "Tilt (x-axis) Raw", "Tilt (y-axis) Raw", ])]
        GROUPBY =  ["Location Description", "Node Id", "Sensor Type"]
        df_tilt_stats = (
            df_tilt.groupby( GROUPBY )["Value"]
            .agg(["count", "min", "max", "mean"])
            .reset_index()
        )
        print(df_tilt_stats)

        order = ["IX-Tilt-Demo 2", "IX-Tilt-Demo 3", "IX-Tilt-Demo 4", "ODS-Demo"]
        df_tilt_stats = df_tilt_stats.copy()
        df_tilt_stats["Location Description"] = pd.Categorical(
            df_tilt_stats["Location Description"],
            categories=order,
            ordered=True
        )
        # sort ตามลำดับ
        df_tilt_stats = df_tilt_stats.sort_values( GROUPBY ).reset_index(drop=True)
        # sort ตามลำดับที่กำหนด
        df_tilt = df_tilt.sort_values( GROUPBY ).reset_index(drop=True)

        df_tilt_ss_grp = df_tilt.groupby( GROUPBY )
        counts = df_tilt_ss_grp.size().reset_index(name="Count")
        print( f'{30*"="} {DAILY} {30*"="}' )
        print( counts)

        n_rows = len(counts) + 1   #  accum rain first
        #####################################################################
        fig, axes = plt.subplots(n_rows, 1, figsize=(12, 2*n_rows),
                                 sharex=True, constrained_layout=True)
        if n_rows == 1:
            axes = [axes]
        args =  [ DAILY, 'RAIN', 'Rain accumulated 24hr',
                    self.dfRAIN['datetime'],self.dfRAIN['ฝน 24 ชม.'] ]
        self.plot_daily_data( args,  axes[0] )
        for cnt, ss_grp in enumerate(df_tilt_ss_grp,start=1):
            #import pdb ;pdb.set_trace()
            SS_TYPE = 'ODS' if cnt>6 else 'TILT' 
            args = [ DAILY, SS_TYPE, ss_grp[0], 
                    ss_grp[1]['datetime'], ss_grp[1]['Value'] ] 
            self.plot_daily_data( args, axes[cnt] )
        dt_obj = datetime.strptime(DAILY, "%Y-%m-%d")
        dt_str = dt_obj.strftime("%A %d %B") + f" {dt_obj.year + 543}"
        plt.tight_layout( rect=[0, 0.03, 1, 0.95] )
        plt.suptitle( f'{dt_str}', fontsize=20, y=0.98, weight="bold" )
        if self.ARGS.popup:
            plt.show()
        else:
            self.DoSaveFig( fig, DAILY )


