import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from RunManager import RunManager, dataTupel
from hgctbplot import Coordinates, TileboardPyplot

import mplhep as hep

hep.style.use("CMS")

hardware_config = {
    2: "A5",
    3: "B12",
}


active_channel = {
    "A5": {
        "chip": 2,
        "channels": np.array([0, 1, 2, 3, 4, 5, 23, 24, 28, 29, 30, 31, 36, 37]),
        "pedestal": 0,
        "plot_dim": (4, 4),
    },
    "B12_0": {
        "chip": 3,
        "channels": np.array([9, 11, 29, 35, 38, 39, 49, 60, 66, 67]),
        "pedestal": 0,
        "plot_dim": (4, 3),
    },
    "B12_1": {
        "chip": 4,
        "channels": np.array([0, 1, 6, 7]),
        "pedestal": 0,
        "plot_dim": (2, 2),
    },
    "G8": {
        "chip": 5,
        "channels": np.array([0, 1, 2, 3, 4, 5, 6, 7]),
        "pedestal": 0,
        "plot_dim": (2, 4),
    }
}




# ----------------------------------------------------------------------------------------------------------------------
#                                            Load data for the plot
# ----------------------------------------------------------------------------------------------------------------------

# Define run mapping dictionary
RUN_MAP = {
    1: "2024-09-16_22-34-48_beamrun_muonss_150",
    2: "2024-09-19_15-11-45_beamrun_muon_250",
    3: "2024-09-21_12-29-11_beamrun_muon_250_magnetOn"
}

run=RUN_MAP[1]

for idx in RUN_MAP:
    run=RUN_MAP[idx]
    preview = False
    preview_size = 10000000 #10000000

    columns_daq = ["trigtime", "adc", "adcm", "channel", "half", "chip", "corruption", "tot", "totflag", "rawdata"]

    rm = RunManager(run, ECONT=False)
    rm.load(
        columns=dataTupel(daq=columns_daq),
        n_files=10,
        preCut_trigtimeCut=True,
        preCut_thresholdCut=True,
        preCut_calibrationChannelCut=False,
        forceReload=False
    )

    df_daq = rm.daq

    ax = plt.gca()


    for tbname, tbconf in active_channel.items():


        coord = Coordinates()
        if tbname == "B12_0" or tbname == "B12_1":
            tbname = "B12"
        
        tb = TileboardPyplot(coord, tbname)

        # df_board = df_daq.query(f"chip == {tbconf['chip']} & channel >= 10 & channel < 72 & ((adc - adcm > 0) | (totflag > 0))").loc[:, ["channel", "adc"]]
        df_board = tbconf["channels"]
        df_cnt = 1000* np.ones(len(df_board)) #df_board.groupby("channel").agg("count")
        print(df_cnt)

        ax.set_aspect("equal")
        tb.draw_outline(ax)
        # tb.hist(ax, df_cnt.index, df_cnt["adc"].values)
        tb.hist(ax, df_board, df_cnt)
        
        tb.label_tiles(ax, values=np.arange(72, dtype=int), radial_offset=-4, angular_offset=0.3)


    plt.show()