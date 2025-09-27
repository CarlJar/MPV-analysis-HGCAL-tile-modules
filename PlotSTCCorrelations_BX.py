import numpy as np
import pandas as pd
import uproot as upr

import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

from PlotUtils import *
from AnalysisConfig import AnalysisConfig

# datapath = "test_data/2024-08-03_14-51-02_ConvGain4_trim_tot_120GeV_muons/"
# datafile = "20240803_152912_phase_ck_6_DAQ.root"

datapath = "/home/fabian/mount/daq/CERN_TB_2024_08/"
datafile = "2024-08-05_18-45-58_ConvGain4_trim_tot_200GeV_electrons_2trains_scint4only_3Tmagnet/" + "20240805_185505_ECONT.root"
# datafile = "2024-08-05_18-32-09_ConvGain4_trim_tot_200GeV_electrons_2trains_scint4only_3Tmagnet/" + "20240805_183247_ECONT.root"
datafile = "2024-08-05_20-28-05_ConvGain4_trim_tot_200GeV_electrons_2trains_scint4only_3Tmagnet_timingcorrect/" + "20240805_202924_ECONT.root"

preview = True
preview_size = 10000000

aconf = AnalysisConfig()
putil = PlotUtils(aconf)

columns = ["trigtime", "globalEventId", "bx", "stcenergy", "stcindex", "largesttc", "chip"]
active_stcs = [1]
bx = np.arange(-7, 8, 1).tolist()
param_of_interest = "stcenergy"

# Open root file
file = upr.open(datapath + datafile)
print(file.keys())

# Load full dataset
if not preview:
    df = file["econt"].arrays(columns, library="pd")

# Load test dataset
else:
    for df_read in file["econt"].iterate(step_size=preview_size, library='pd'):
        df = df_read
        break

df = df.query(f"trigtime > 40 & bx in {bx} & stcindex in {active_stcs}")

df_chip0 = df.query(f"chip == 0")
df_chip1 = df.query(f"chip == 1")

df_joined = df_chip0.merge(df_chip1, on=["globalEventId"], suffixes=("_chip0", "_chip1"), how="inner")

# Compute correlations
pearson_corr = np.zeros((len(bx), len(bx)))

# for stc_sel in active_stcs:
#     fig, ax = plt.subplots(1, 1)
#     df_sel = df_joined.query(f"stcindex_chip0 == {stc_sel} & stcindex_chip1 == {stc_sel}")
#     putil.Hist2D(df_sel, ax, f"{param_of_interest}_chip0", f"{param_of_interest}_chip1", norm=mpl.colors.LogNorm())

fig_pear, ax_pear = plt.subplots(1, 1)
fig_pear.suptitle(f"Pearson correlation of STC events", fontweight="bold")
ax_pear.set_title(datafile.split("/")[0] + (f"\nfirst {preview_size/1000}k events" if preview else ""), fontsize="small")

def cov(x1, x2):
    return np.sum((x1 - np.mean(x1)) * (x2 - np.mean(x2))) / x1.shape[0]


for i0, ch0 in enumerate(bx):
    for i1, ch1 in enumerate(bx):
        df_sel = df_joined.query(f"bx_chip0 == {ch0} & bx_chip1 == {ch1}")
        pc = cov(df_sel[f"{param_of_interest}_chip0"], df_sel[f"{param_of_interest}_chip1"]) / \
             np.sqrt(cov(df_sel[f"{param_of_interest}_chip0"], df_sel[f"{param_of_interest}_chip0"])
                     * cov(df_sel[f"{param_of_interest}_chip1"], df_sel[f"{param_of_interest}_chip1"]))
        pearson_corr[i0, i1] = pc
        ax_pear.text(i0, i1, "{:.02f}".format(pc), ha="center", va="center", color="w")
        print(f"{ch0}, {ch1}, {pc:.2f}")

print(pearson_corr)
im_pear = ax_pear.imshow(pearson_corr.T, vmin=-1, vmax=1, cmap="bwr")

divider = make_axes_locatable(ax_pear)
cax = divider.append_axes('right', size='5%', pad=0.05)
fig_pear.colorbar(im_pear, cax=cax, orientation='vertical')

ax_pear.set_xticks(np.arange(len(bx)), labels=bx)
ax_pear.set_yticks(np.arange(len(bx)), labels=bx)

ax_pear.set_xlabel("BX of TB3_A5_4 (chip 0)")
ax_pear.set_ylabel("BX of TB3_A5_1 (chip 1)")

plt.show()