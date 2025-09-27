import os
import matplotlib as mpl
import matplotlib.pyplot as plt
import yaml
from RunManager import RunManager, findChipHalfConstellations, dataTupel
from PlotUtils import PlotUtils
from AnalysisConfig import AnalysisConfig
aconf = AnalysisConfig()
putil = PlotUtils(aconf)

def print_parameters(trigtimecut_low, trigtimecut_high, adcthreshold, chip, half):
    output = f"""- trigtimecut_low: {trigtimecut_low}
  trigtimecut_high: {trigtimecut_high}
  adcthreshold: {adcthreshold}
  chip: {chip}
  half: {half}"""
    print(output)
class PlotContainer:
    def __init__(self, runName, configYaml = 'config/dataset_config.yaml'):
        self.runName = runName
        self.configYaml = configYaml
        self.fig = None      # Speichert das Figure-Objekt
        self.ax = []         # Liste von Achsen
        self.vlow_lines = []       # Liste für 'vlow' Linien
        self.vhigh_lines = []      # Liste für 'vhigh' Linien
        self.hlow_lines = []       # Liste für 'hlow' Linien
        self.chip = None
        self.half = None
        self.config = {
            'trigtimecut_low': 0,
            'trigtimecut_high': 0,
            'adcthreshold': 0
        }
        self.df = None

    def update_yaml(self):
        """Aktualisiert die trigtimecut und adcthreshold-Werte in der YAML-Datei
        Args:
            yaml_file (str): Der Pfad zur YAML-Datei.
            run_name (str): Der Name des Runs, dessen Konfigurationen aktualisiert werden sollen.
            new_configs (list): Eine Liste von Dictionaries mit den neuen Konfigurationen.
        """
        # YAML-Datei laden
        with open(self.configYaml, 'r') as file:
            data = yaml.safe_load(file)
        # Durch die Datensätze iterieren, um den entsprechenden Run zu finden
        for dataset in data['datasets']:
            if dataset['_run'] == self.runName:
                # Durch die Konfigurationen iterieren, um das richtige zu finden
                configUpdated = False
                for config in dataset['_configs']:
                    if config['chip'] == self.chip and config['half'] == self.half:
                        # Werte aktualisieren
                        config.update(self.config)
                        configUpdated = True
                        break
                if not configUpdated:
                    # if there is no config for this chip/half: append a new one
                    newConfElem = self.config.copy()
                    newConfElem['chip'] = self.chip
                    newConfElem['half'] = self.half
                    dataset['_configs'].append(newConfElem)
                
                break
        # Änderungen in der YAML-Datei speichern
        with open(self.configYaml, 'w') as file:
            yaml.dump(data, file)

def checkForConfig(run, path, configYaml = 'config/dataset_config.yaml'):
    # YAML-Datei laden
    with open(configYaml, 'r') as file:
        data = yaml.safe_load(file)
    foundThisRun = False
    for dataset in data['datasets']:
            if dataset['_run'] == run:
                foundThisRun = True
                break
    if not foundThisRun:
        data['datasets'].append({'_run': run,'_path': path, '_configs':[]})
        # Änderungen in der YAML-Datei speichern
        with open(configYaml, 'w') as file:
            yaml.dump(data, file)
        print(f""" created a new config entry for: {run}""")

run = "2024-09-14_23-04-13_beamrun_muon_150"
run = "2024-09-16_17-13-51_beamrun_muons"
run = "2024-09-16_22-34-48_beamrun_muonss_150"
run = "2024-09-19_22-31-00_beamrun_electron_200_test_repeater_TC8_correct"
run = "2024-09-20_10-44-00_beamrun_muon_250_test_repeater_TC8_correct"
run = "2024-09-19_21-47-49_beamrun_electron_200_test_repeater"
run = "2024-09-19_20-47-19_beamrun_electron_100_test_repeater"
run = "2024-09-19_20-36-36_beamrun_electron_100_test_repeater_timingtest" # no configs added
run = "2024-09-19_18-44-18_beamrun_electron_200"
run = "2024-09-19_15-11-45_beamrun_muon_250"
run = "2024-09-19_14-35-41_beamrun_muon_250_timingtest"
run = "2024-09-18_20-34-45_beamrun_electrons_200"
run = "2024-09-18_18-41-07_beamrun_electrons_200_phase_test"
run = "2024-09-18_14-57-36_beamrun_electrons_200"
run = "2024-09-18_14-55-16_beamrun_electrons_200_timingtest"
run = "2024-09-18_12-46-08_beamrun_electrons_200"
run = "2024-09-17_11-15-16_beamrun_electrons_200_newSTCMapping"
run = "2024-09-17_19-21-01_beamrun_muon_150_1709"
run = "2024-09-17_10-57-31_beamrun_electrons_200_newSTCMapping_timingtest"
run = "2024-09-16_20-32-33_beamrun_electrons_200"
run = "2024-09-18_12-37-49_beamrun_electrons_200"
run = "2024-09-16_15-28-58_beamrun_electrons_200"
run = "2024-08-03_23-57-30_ConvGain4_trim_tot_120GeV_muon_2xCoincidence"
#run = ""

# Test Beam 2024-08 - ALPAH train only
run = "2024-08-03_19-04-13_ConvGain4_trim_tot_200GeV_electrons_trigthres"
run = "2024-08-03_23-57-30_ConvGain4_trim_tot_120GeV_muon_2xCoincidence"
run = "2024-08-04_11-59-14_ConvGain4_trim_tot_200GeV_electron_2xCoincidence"
run = "2024-08-04_16-54-19_ConvGain4_trim_tot_120GeV_muon_2xCoincidence"
run = "2024-08-04_22-08-43_ConvGain4_trim_tot_120GeV_muon_2xCoincidence_magnet_ramping_down"
run = "2024-08-04_23-06-35_ConvGain4_trim_tot_120GeV_muon_2xCoincidence_magnet_off"

# Test Beam 2024-08 - ALPHA + BRAVO train
run = "2024-08-05_20-28-05_ConvGain4_trim_tot_200GeV_electrons_2trains_scint4only_3Tmagnet_timingcorrect"
run = "2024-08-06_01-53-34_ConvGain4_trim_tot_muons_2trains_scint4only_3Tmagnet"
run = "2024-08-06_07-14-02_ConvGain4_trim_tot_muons_2trains_scint4only_magnet_ramp_down"
run = "2024-08-06_08-49-25_ConvGain4_trim_tot_muons_2trains_scint4only_magnet_off"
run = "2024-08-06_14-56-19_ConvGain4_trim_tot_200GeV_2trains_scint4only_3Tmagnet_90deg"

# Test Beam 2024-09 - BRAVO Train muon runs
run = "2024-09-16_22-34-48_beamrun_muonss_150"
# run = "2024-09-17_19-21-01_beamrun_muon_150_1709"
# run = "2024-09-19_15-11-45_beamrun_muon_250"
# run = "2024-09-21_12-29-11_beamrun_muon_250_magnetOn"

# ask for run if run is empty: ""
if run == "":
    run = input("pls enter run to find cuts: ")

checkForConfig(path = 'CERN_TB_2024_09', run = run)
# checkForConfig(path = 'CERN_TB_2024_08', run = run)

rm = RunManager(run, ECONT = False)

rm.load(
    columns=dataTupel(daq=["adc", "tot", "adcm", "trigtime", "corruption", "channel", "half", "chip"]),
    pre_cut=dataTupel(daq = "(corruption == 0) & (trigtime > 0)"),
    #pre_cut="(corruption == 0) & (trigtime > 0)",# & (channel == 28) & (half == 0) & (chip == 0)", # TODO: add the trigtime-cuts and threshold cuts
    #post_cut=dataTupel(daq="(trigtime < 30) & (trigtime > 10)", econt="(globalEventId > 16217809971000)"),
    # preview_size=100000,
    n_files=2,
    #forceReload=True,
    preCut_trigtimeCut=False,
    preCut_thresholdCut=False,
    preCut_calibrationChannelCut=True
)
runconfig = rm.get_runconfig()

print(rm.daq)
print(rm.econt)

allChipHalfConstellations = findChipHalfConstellations(rm.daq)

plots = []
for data in allChipHalfConstellations:
    plot = PlotContainer(run)
    plot.chip = data['chip']
    plot.half = data['half']
    plots.append(plot)

#print the cuts for all relevant config elements
for plot in plots:
    confs = [config for config in runconfig["_configs"] if (config["chip"] == plot.chip and config["half"] == plot.half)]
    if len(confs) > 1:
        print(f"""WARNING: More than 1 config for chip: {plot.chip}, half: {plot.half}""")
    if len(confs) >= 1:
        plot.config = confs[0]

    plot.df = rm.daq.query(f"chip == {plot.chip} & half == {plot.half}")

    plot.fig, plot.ax, = plt.subplots(1, 3)
    plot.fig.suptitle(f"""chip: {plot.chip}, half: {plot.half}""")
    
    x,y = putil.Hist2D(plot.df, plot.ax[0], "trigtime", "adc", norm=mpl.colors.LogNorm())
    putil.Hist2D(plot.df, plot.ax[1], "trigtime", "adcm", norm=mpl.colors.LogNorm())#, x_range = x, y_range = y)
    putil.Hist2D(plot.df, plot.ax[2], "trigtime", "tot", norm=mpl.colors.LogNorm())#, x_range = x, y_range = y)

    for i_ax in plot.ax:
        i_ax.set_xlim(x[-1]-32, x[-1]+1)
    
    # plot the cuts
    plot.vlow_lines.append(plot.ax[0].axvline(plot.config["trigtimecut_low"], color="r"))
    plot.vhigh_lines.append(plot.ax[0].axvline(plot.config["trigtimecut_high"], color="r"))
    plot.hlow_lines.append(plot.ax[0].axhline(plot.config["adcthreshold"], color="r"))
    plot.vlow_lines.append(plot.ax[1].axvline(plot.config["trigtimecut_low"], color="r"))
    plot.vhigh_lines.append(plot.ax[1].axvline(plot.config["trigtimecut_high"], color="r"))
    plot.hlow_lines.append(plot.ax[1].axhline(plot.config["adcthreshold"], color="r"))
    plot.vlow_lines.append(plot.ax[2].axvline(plot.config["trigtimecut_low"], color="r"))
    plot.vhigh_lines.append(plot.ax[2].axvline(plot.config["trigtimecut_high"], color="r"))

    plot.fig.set_figwidth(12)
    plot.fig.tight_layout()

for plot in plots:
    def create_on_figure_enter_handler(current_plot):
        # Closure, die den aktuellen Plot speichert
        def on_figure_enter(event):
            if event.xdata is not None and event.ydata is not None:
                x, y = round(event.xdata), round(event.ydata)
            else: x,y = None, None
            if event.key == 'y':    # trigtimecut_low
                for line in current_plot.vlow_lines:
                    line.set_xdata([x])
                current_plot.config['trigtimecut_low'] = x
            elif event.key == 'x':  # trigtimecut_high
                for line in current_plot.vhigh_lines:
                    line.set_xdata([x])
                current_plot.config['trigtimecut_high'] = x
            elif event.key == 'c':  # adcthreshold
                for line in current_plot.hlow_lines:
                    line.set_ydata([y])
                current_plot.config['adcthreshold'] = y
            elif event.key == 'm':  # save for this config
                current_plot.update_yaml()
            current_plot.fig.canvas.draw()
        return on_figure_enter
    plot.fig.canvas.mpl_connect('key_press_event', create_on_figure_enter_handler(plot))


img_folder = "findCuts_output/"
if not os.path.isdir(img_folder):
    os.mkdir(img_folder)

img_subfolder = os.path.join(img_folder, run)
if not os.path.isdir(img_subfolder):
    os.mkdir(img_subfolder)

for plot in plots:
    plot.fig.savefig(os.path.join(img_subfolder, f"chip{plot.chip}_half{plot.half}.png"))


plt.show()