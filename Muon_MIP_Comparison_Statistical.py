import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import chi2, norm

# ---------------------------
# Konfiguration (anpassen)
# ---------------------------
BASE_DATA_PATH = '/home/carlj/BA_local_data/CERN_TB_2024_09_Analysis/'
RUNS = {
    "muon_150": "2024-09-16_22-34-48_beamrun_muonss_150",
    "muon_250": "2024-09-19_15-11-45_beamrun_muon_250",
    "muon_250_magnetOn": "2024-09-21_12-29-11_beamrun_muon_250_magnetOn"
}
OUTPUT_DIR = os.path.join(BASE_DATA_PATH, "comparison_plots_statistical_thesis")
os.makedirs(OUTPUT_DIR, exist_ok=True)

CHIPS_ALL = [2, 3, 4]
CHIP_SETS = [CHIPS_ALL, [2], [3,4]]
CHIP_SET_NAMES = ["All_Chips", "Chip_2", "Chips_3_and_4"]

# ---------------------------
# Hilfsfunktionen
# ---------------------------
def load_df(run_key):
    path = os.path.join(BASE_DATA_PATH, RUNS[run_key], "analysis_results", "simplified_results.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        print(f"Warning: {path} not found")
        return None

def symmetric_err(df):
    # aus unteren/oberen Fehlern einen symmetrischen Fehler machen
    # falls Spalten fehlen -> KeyError, dann kurz auffangen
    low = df["mpv_err_lower"].values
    up  = df["mpv_err_upper"].values
    return 0.5 * (np.abs(low) + np.abs(up))

def compute_global_stats(pulls, chi2_contribs):
    N = len(pulls)
    chi2_tot = np.sum(chi2_contribs) if len(chi2_contribs)>0 else 0.0
    dof = N
    pval = 1.0 - chi2.cdf(chi2_tot, dof) if dof>0 else 1.0
    # two-sided Gaussian sigma: convert p -> Z
    # for very small p -> isf(0) -> inf (huge significance)
    global_sigma = norm.isf(pval/2) if (0 < pval < 1) else (0.0 if pval >= 1.0 else np.inf)
    mean_pull = np.mean(pulls) if N>0 else np.nan
    se_mean = (1.0/np.sqrt(N)) if N>0 else np.nan
    rms_pull = np.sqrt(np.mean(pulls**2)) if N>0 else np.nan
    frac_gt2 = np.mean(np.abs(pulls) > 2) if N>0 else np.nan
    frac_gt3 = np.mean(np.abs(pulls) > 3) if N>0 else np.nan
    return {
        "N": N, "chi2_tot": chi2_tot, "dof": dof, "pval": pval,
        "global_sigma": global_sigma, "mean_pull": mean_pull, "se_mean": se_mean,
        "rms_pull": rms_pull, "frac_gt2": frac_gt2, "frac_gt3": frac_gt3
    }

# ---------------------------
# Plot / Vergleichsfunktion
# ---------------------------
def compare_runs(dfA, dfB, titleA, titleB, chips, set_name):
    # Sammelvariablen
    pulls_all = []
    chi2_contribs = []
    channels_all = []

    # Erzeuge Scatter-Plot (MPV_A vs MPV_B) und Pull-Hist
    fig, (ax_scatter, ax_pull) = plt.subplots(2,1, figsize=(10,12), gridspec_kw={"height_ratios":[3,1]}, sharex=False)
    # fig.suptitle(f"Comparison of MPV Values: {titleA.replace('_', ' ')} vs {titleB.replace('_', ' ')}", fontsize=16, y=0.98)

    for chip in chips:
        dA = dfA[dfA["chip"] == chip].set_index("channel")
        dB = dfB[dfB["chip"] == chip].set_index("channel")
        common = dA.index.intersection(dB.index)
        if len(common) == 0:
            continue
        dA = dA.loc[common]; dB = dB.loc[common]

        x = dA["mpv"].values
        y = dB["mpv"].values
        sx = symmetric_err(dA)
        sy = symmetric_err(dB)
        
        sx_low = np.abs(dA["mpv_err_lower"].values)
        sx_up  = np.abs(dA["mpv_err_upper"].values)
        sy_low = np.abs(dB["mpv_err_lower"].values)
        sy_up  = np.abs(dB["mpv_err_upper"].values)

        
        # kombiniertes sigma pro Kanal
        s_comb = np.sqrt(sx**2 + sy**2)
        # falls s_comb == 0 für einige Kanäle -> markiere und überspringe in Pulls
        mask_valid = s_comb > 0
        if not np.any(mask_valid):
            continue

        # Pulls und chi2 Beiträge
        pulls = (y[mask_valid] - x[mask_valid]) / s_comb[mask_valid]
        chi2s = pulls**2

        # Sammeln
        pulls_all.append(pulls)
        chi2_contribs.append(chi2s)
        channels = [f"ch{chip}:{ch}" for ch in common[mask_valid]]
        channels_all.append(channels)

        # Scatter (plot mit Fehlerbalken)
        # ax_scatter.errorbar(x, y, xerr=sx, yerr=sy, fmt='o', ms=4, alpha=0.8, label=f"Chip {chip}")
        ax_scatter.errorbar(
            x, y,
            xerr=[sx_low, sx_up],
            yerr=[sy_low, sy_up],
            fmt='o', ms=4, alpha=0.8, label=f"Chip {chip}"
        )
        
        
        
        
    # Konkateniere Listen
    if len(pulls_all) == 0:
        print(f"No common channels for set {set_name} in {titleA} vs {titleB}")
        plt.close(fig)
        return
    pulls_all = np.concatenate(pulls_all)
    chi2_contribs = np.concatenate(chi2_contribs)
    channels_all = sum(channels_all, [])  # flache Liste

    # Globale Kennzahlen
    stats = compute_global_stats(pulls_all, chi2_contribs)

    # Scatter: Diagonale, Limits anpassen
    ax_scatter.plot([ax_scatter.get_xlim()[0], ax_scatter.get_xlim()[1]],
                    [ax_scatter.get_xlim()[0], ax_scatter.get_xlim()[1]], '--', color='gray', label='Equality')
    ax_scatter.set_xlabel(f"MPV ({titleA.replace('_', ' ')}) [ADC value]", fontsize=14)
    ax_scatter.set_ylabel(f"MPV ({titleB.replace('_', ' ')}) [ADC value]", fontsize=14)
    ax_scatter.set_title(f"Comparison of MPV Values: {titleA.replace('_', ' ')} vs {titleB.replace('_', ' ')}", fontsize=16)
    ax_scatter.legend()
    ax_scatter.grid(alpha=0.25)

    # Summary-Textbox (kurz & thesis-geeignet)
    txt = (
        f"N = {stats['N']}\n"
        f"χ²/dof = {stats['chi2_tot']:.1f}/{stats['dof']}\n"
        f"Global σ (χ²→Z) = {stats['global_sigma']:.2f}\n"
        f"mean pull = {stats['mean_pull']:.3f} ± {stats['se_mean']:.3f} (σ)\n"
        f"RMS = {stats['rms_pull']:.3f} (σ)\n"
        f"Frac >2σ / >3σ = {100*stats['frac_gt2']:.1f}% / {100*stats['frac_gt3']:.2f}%"
    )
    ax_scatter.text(0.02, 0.95, txt, transform=ax_scatter.transAxes, fontsize=10,
                    va='top', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

    # Pull-Histogramm
    bins = np.linspace(-6,6,49)
    ax_pull.axvline(stats['mean_pull'], color='red', linestyle='-', label=f"Mean Pull = {stats['mean_pull']:.3f} (σ)")
    ax_pull.hist(pulls_all, bins=bins, alpha=0.8)
    ax_pull.axvspan(-1,1, color='green', alpha=0.3, label="±1σ")
    ax_pull.axvspan(-2,2, color='yellow', alpha=0.15, label="±2σ")
    ax_pull.axvline(0, color='k', linestyle='--')
    ax_pull.set_xlabel("Pull (σ)")
    ax_pull.set_ylabel("Channel count")
    ax_pull.grid(alpha=0.2)
    ax_pull.legend()

    # # ===== Top-5 Kanäle nach χ²-Beitrag (nützlich für Appendix) =====
    # # Top-5 Kanäle nach χ²-Beitrag (nützlich für Appendix)
    # order = np.argsort(chi2_contribs)[::-1]
    # top = min(5, len(order))
    # top_lines = [f"{channels_all[order[i]]}: χ²={chi2_contribs[order[i]]:.2f}, pull={pulls_all[order[i]]:.2f}"
    #              for i in range(top)]
    # # kleine Annotation unter Histogramm
    # ax_pull.text(0.02, 0.95, "Top contributors:\n" + "\n".join(top_lines),
    #              transform=ax_pull.transAxes, fontsize=9, va='top', bbox=dict(facecolor='white', alpha=0.8))

    # Speichern
    fname = os.path.join(OUTPUT_DIR, f"Comparison_{titleA}_vs_{titleB}_{set_name}.png")
    plt.savefig(fname, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved {fname}. Summary: global σ={stats['global_sigma']:.2f}, RMS={stats['rms_pull']:.2f}")

# ---------------------------
# Main: Vergleiche erstellen
# ---------------------------
def main():
    dfs = {k: load_df(k) for k in RUNS}
    # nur gültige laden
    dfs = {k: v for k,v in dfs.items() if v is not None}
    if len(dfs) < 2:
        print("Need at least two valid runs.")
        return

    comparisons = [
        ("muon_150", "muon_250"),
        ("muon_250", "muon_250_magnetOn"),
        ("muon_150", "muon_250_magnetOn")
    ]
    for a,b in comparisons:
        if a in dfs and b in dfs:
            for chips, name in zip(CHIP_SETS, CHIP_SET_NAMES):
                compare_runs(dfs[a], dfs[b], a, b, chips, name)

if __name__ == "__main__":
    main()