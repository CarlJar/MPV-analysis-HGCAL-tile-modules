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
}

channels = np.concatenate([
    active_channel["B12_0"]["channels"],
    active_channel["B12_1"]["channels"] + 72  # Offset for chip 4 channels
])

# Build mapping array: 3 for B12_0, 2 for B12_1
mapping = np.concatenate([
    np.full_like(active_channel["B12_0"]["channels"], 7),
    np.full_like(active_channel["B12_1"]["channels"], 5)
])

print("Channels:", channels)
print("Mapping:", mapping)


# ----------------------------------------------------------------------------------------------------------------------
#                                            Load data for the plot
# ----------------------------------------------------------------------------------------------------------------------

# Define run mapping dictionary
RUN_MAP = {
    1: "2024-09-16_22-34-48_beamrun_muonss_150",
    # 2: "2024-09-19_15-11-45_beamrun_muon_250",
    # 3: "2024-09-21_12-29-11_beamrun_muon_250_magnetOn"
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


    coord = Coordinates()
    tbname = "B12"
    
    tb = TileboardPyplot(coord, tbname)

    # df_board = df_daq.query(f"chip == {tbconf['chip']} & channel >= 10 & channel < 72 & ((adc - adcm > 0) | (totflag > 0))").loc[:, ["channel", "adc"]]
    df_board = channels
    df_cnt = mapping #df_board.groupby("channel").agg("count")
    print(df_cnt)

    ax.set_aspect("equal")
    tb.draw_outline(ax)
    # tb.hist(ax, df_cnt.index, df_cnt["adc"].values)
    tb.hist(ax, df_board, df_cnt, cmap=plt.cm.get_cmap("tab10", 10))
    
    tb.label_tiles(ax, values=np.arange(72+36, dtype=int), radial_offset=-4, angular_offset=0.32, fontsize=12)

    ax.set_xlabel("X position [mm]")   # or just "X" if no units
    ax.set_ylabel("Y position [mm]")   # or just "Y"
    ax.set_title(f"Active channels on {tbname}")
    
    plt.savefig(f"active_channels_{tbname}.pdf", bbox_inches='tight', dpi=300)
    plt.show()