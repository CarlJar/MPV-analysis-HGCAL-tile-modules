import os
import re
import yaml
import uproot as upr
import pandas as pd
import __main__
from pathlib import Path
import hashlib
import json

# find allChipHalfConstellations of the data
def findChipHalfConstellations(dataframe = pd.DataFrame({})):
    allChipsInDF = dataframe["chip"].unique().tolist()
    allChipHalfConstellations = []

    for chipnumber in allChipsInDF:
        allHalfsForThisChip = dataframe.query(f"chip == {chipnumber}")["half"].unique().tolist()
        for half in allHalfsForThisChip:
            allChipHalfConstellations.append({"chip": chipnumber, "half": half})
    return allChipHalfConstellations

# filter for relevant config elements based on data
def filterConfigElements(configElements = [], dataframe = pd.DataFrame({})):
    if dataframe is None or configElements is None: return []


    allChipHalfConstellations = findChipHalfConstellations(dataframe)

    # filter
    validConfigs = []
    for conf in configElements:
        for constellation in allChipHalfConstellations:
            if ( conf["chip"] == constellation["chip"] and conf["half"] == constellation["half"] ): validConfigs.append(conf)

    return validConfigs

class dataTupel:
    def __init__(self, daq = None, econt = None):
        self.DAQ = daq
        self.ECONT = econt
class RunInfo:
    def __init__(self, 
            DAQ_active=False, 
            ECONT_active=False, 
            preview_size=None, 
            n_files=None, 
            columns=None, 
            pre_cut=None, 
            post_cut=None,
            preCut_trigtimeCut=True,
            preCut_thresholdCut=True,
            preCut_calibrationChannelCut=True,
            runConfig=None
            ):
        #self.run_name = run_name
        self.DAQ_active = DAQ_active
        self.ECONT_active = ECONT_active
        self.preview_size = preview_size
        self.n_files = n_files
        self.columns = columns if columns is not None else dataTupel([],[])
        self.pre_cut = pre_cut if pre_cut is not None else dataTupel("","")
        self.post_cut = post_cut if post_cut is not None else dataTupel("","")
        self.preCut_trigtimeCut = preCut_trigtimeCut
        self.preCut_thresholdCut = preCut_thresholdCut
        self.preCut_calibrationChannelCut = preCut_calibrationChannelCut
        self.runConfig = runConfig

    def preCut_DAQ_getString(self):
        preCutString = self.pre_cut.DAQ if self.pre_cut.DAQ is not None and len(self.pre_cut.DAQ) > 3 else ""
        if(self.preCut_calibrationChannelCut):
            preCutString += " & (channel >= 0) & (channel <= 35)"
        # find new precut elements depending on trigtimeCut and thresholdCut
        if (self.preCut_trigtimeCut or self.preCut_thresholdCut) and self.runConfig is not None :
            precutMods = []
            for conf in self.runConfig["_configs"]:
                precutMod = f"""(chip == {conf["chip"]}) & (half == {conf["half"]})"""
                if self.preCut_trigtimeCut:
                    precutMod += f""" & (trigtime >= {conf["trigtimecut_low"]}) & (trigtime < {conf["trigtimecut_high"]})"""
                if self.preCut_thresholdCut:
                    precutMod += f""" & (adc >= {conf["adcthreshold"]})"""
                precutMods.append(precutMod)
            # modify the pre_cut
            if len(preCutString) > 3: preCutString += " & "
            modifiedPreCut = ""
            for precutMod in precutMods:
                if len(modifiedPreCut) > 3: modifiedPreCut+= " | "
                modifiedPreCut+=( preCutString + precutMod)
            return modifiedPreCut
        else: return preCutString
        
    def preCut_ECONT_getString(self):
        return self.pre_cut.ECONT

    def getHash(self, tag = "DAQ"):
        dataSelection = None
        if tag == "DAQ":
            dataSelection = {
                'n_files': self.n_files,
                'preview_size': self.preview_size,
                'columns': self.columns.DAQ,
                'pre_cut': self.preCut_DAQ_getString()
            }
        elif tag == "ECONT":
            dataSelection = {
                'n_files': self.n_files,
                'preview_size': self.preview_size,
                'columns': self.columns.ECONT,
                'pre_cut': self.preCut_ECONT_getString()
            }
        dict_str = json.dumps(dataSelection, sort_keys=True)
        hash = hashlib.sha256(dict_str.encode()).hexdigest()
        return hash, dataSelection



class RunManager:
    DATA_FILE_PATTERN = re.compile(r"(?P<date>\d{8})_(?P<time>\d{6})_?(?P<info>\w*)_(?P<type>\w{3,5}).root")
    DEFAULT_COLUMNS = {
        'DAQ': ["globalEventId"],
        'ECONT': ["globalEventId"],
    }

    def __init__(self, 
            run_name, 
            DAQ = True, 
            ECONT = True, 
            preCut_trigtimeCut=True,
            preCut_thresholdCut=True,
            preCut_calibrationChannelCut=True
            ):
        self.run_name = run_name
        self.run_info = RunInfo(DAQ_active=DAQ, ECONT_active=ECONT)
        self.daq = None
        self.econt = None
        self.BASE_PATH = ""
        self.run_folder = ""
        self.runManConfigPath = "config/runmanager_config.yaml"
        self.runManConfig = None
        
        # Read runconfig YAML file
        try:
            with open(self.runManConfigPath, 'r') as stream:
                self.runManConfig = yaml.safe_load(stream)
            if 'runmanager' in self.runManConfig:
                self.runManConfig = self.runManConfig['runmanager']
            else: raise ValueError('no "runmanager" attribute in runmanager_config.yaml')
        except Exception as e:
            self.runManConfig = None
            print("runmanager_config.yaml not loaded: " + str(e))
        
        # get BasePath
        if self.runManConfig and 'BASE_PATH' in self.runManConfig:
            self.BASE_PATH = self.runManConfig['BASE_PATH']


    def load(self, 
            columns = dataTupel(),
            pre_cut = dataTupel(),
            post_cut = dataTupel(), 
            preview_size=None,
            n_files=None,
            forceReload=False,
            preCut_trigtimeCut=True,
            preCut_thresholdCut=True,
            preCut_calibrationChannelCut=True
            ):
        self.run_info.preview_size = preview_size
        self.run_info.n_files = n_files
        self.run_info.preCut_trigtimeCut = preCut_trigtimeCut
        self.run_info.preCut_thresholdCut = preCut_thresholdCut
        self.run_info.preCut_calibrationChannelCut = preCut_calibrationChannelCut

        # handle requested columns
        self.run_info.columns = dataTupel(
            daq = ( RunManager.DEFAULT_COLUMNS['DAQ'] + columns.DAQ) if columns.DAQ is not None else RunManager.DEFAULT_COLUMNS['DAQ'],
            econt = ( RunManager.DEFAULT_COLUMNS['ECONT'] + columns.ECONT) if columns.ECONT is not None else RunManager.DEFAULT_COLUMNS['ECONT']
        )

        self.run_info.pre_cut = pre_cut
        self.run_info.post_cut = post_cut

        self.run_info.runConfig = self.get_runconfig()

        if self.run_info.runConfig is not None and not self.runManConfig["ignoreDataConfigPath"]:
            if "_path" in self.run_info.runConfig:
                self.run_folder = self.run_info.runConfig["_path"]
        else: self.run_folder = ""

        # find new precut elements depending on trigtimeCut and thresholdCut
        #self.__update_PreCutString(trigtimeCut = preCut_trigtimeCut, thresholdCut = preCut_thresholdCut, calibrationChannelCut = preCut_calibrationChannelCut)
        
        # try to load from cache
        daqCached = False
        if not forceReload and self.run_info.DAQ_active: self.daq, daqCached = self.__load_from_cache("DAQ")
        econtCached = False
        if not forceReload and self.run_info.ECONT_active: self.econt, econtCached = self.__load_from_cache("ECONT")

        # load from file if it is 
        if daqCached is False and self.run_info.DAQ_active:
            self.daq = self.__loadFiles("DAQ", self.run_info.n_files, self.run_info.preview_size, self.run_info.columns.DAQ)
            #self.daq = self.__postCut(self.daq, "DAQ")

        if econtCached is False and self.run_info.ECONT_active:
            self.econt = self.__loadFiles("ECONT", self.run_info.n_files, self.run_info.preview_size, self.run_info.columns.ECONT)
            #self.econt = self.__postCut(self.econt, "ECONT")
        
        self.__to_cache()

        self.daq = self.__postCut(self.daq, "DAQ")
        self.econt = self.__postCut(self.econt, "ECONT")

    def __loadFiles(self, typeGroup, n, preview_size, columns):
        # Explore run folders in path
            i_file = 0

            dataframe = None
            filepath = None

            # to open DAQ files
            if(typeGroup == "DAQ"): filepath = "unpacker_data/hgcroc"
            if(typeGroup == "ECONT"): filepath = "econt"

            for fname in os.scandir(os.path.join(self.BASE_PATH, self.run_folder, self.run_name)):
                # Find files matching the expected pattern
                match = RunManager.DATA_FILE_PATTERN.match(fname.name)
                if fname.is_file() and match is not None and match.group("type") == typeGroup:
                    # Open the root file
                    file = upr.open(fname.path)
                    if filepath is not None: file = file[filepath]
                    # Load full dataset
                    if preview_size is None:
                        # cut = "" crashes
                        preCutStr = None
                        if(typeGroup == "DAQ"): preCutStr = self.run_info.preCut_DAQ_getString()
                        if(typeGroup == "ECONT"): preCutStr = self.run_info.preCut_ECONT_getString()
                        
                        if preCutStr is not None and len(preCutStr) > 3: 
                            df_tmp = file.arrays(columns, cut=preCutStr, library="pd")
                        else:
                            df_tmp = file.arrays(columns, library="pd")
                    # Load test dataset
                    else:
                        # cut = "" crashes
                        if len(self.run_info["pre_cut_string"]) > 3: 
                            for df_read in file.iterate(
                                    expressions=columns, cut=self.run_info["pre_cut_string"],
                                    step_size=preview_size, library='pd'):
                                df_tmp = df_read
                                break
                        else:
                            for df_read in file.iterate(
                                    expressions=columns,
                                    step_size=preview_size, library='pd'):
                                df_tmp = df_read
                                break
                    # append to destination
                    if dataframe is None:
                        dataframe = df_tmp
                    else:
                        dataframe = pd.concat([dataframe, df_tmp], ignore_index=True)
                    # Status
                    print(f"{i_file}: Loaded file '{fname.name}'")
                    print(f"Entries in data frame: {dataframe.shape[0]} (added {df_tmp.shape[0]} entries in this step)")
                    # Increase file counter
                    i_file += 1
                    if i_file == n:
                        break
            return dataframe
    
    def __postCut(self, dataframe, tag=""):

        if tag == "ECONT":
            post_cut_string = self.run_info.post_cut.ECONT
            if post_cut_string is not None and len(post_cut_string) > 3:
                dataframe = dataframe.query(post_cut_string)
        if tag == "DAQ":
            # Correct channel number
            # Correction for calibration-channel:
            # Bedingung 1: chip == 0 und half == 1
            dataframe.loc[(dataframe['channel'] == -1), 'channel'] = 0 + dataframe["chip"].astype('int32')*10000 + dataframe["half"].astype('int32')*10 + 1000000
            dataframe.loc[(dataframe['channel'] == 36), 'channel'] = 1 + dataframe["chip"].astype('int32')*10000 + dataframe["half"].astype('int32')*10 + 1000000
            dataframe.loc[(dataframe['channel'] == 37), 'channel'] = 2 + dataframe["chip"].astype('int32')*10000 + dataframe["half"].astype('int32')*10 + 1000000
            dataframe.loc[(dataframe['channel'] == 38), 'channel'] = 3 + dataframe["chip"].astype('int32')*10000 + dataframe["half"].astype('int32')*10 + 1000000
            # channel number for analysis
            dataframe.loc[(dataframe['channel'] >= 0) & (dataframe['channel'] <= 35), 'channel'] = dataframe["channel"] + 36 * dataframe["half"]
            # Correct bx uint16 to int16df
            if 'bx' in dataframe: dataframe = dataframe.astype({'bx': 'int16'})

            # TODO: tot 10 to 12 bit conversion

            # Apply selection if required
            post_cut_string = self.run_info.post_cut.DAQ
            if post_cut_string is not None and len(post_cut_string) > 3:
                dataframe = dataframe.query(post_cut_string)
        
        return dataframe

    def get_run_name(self):
        return self.run_name

    def get_run_info(self):
        if self.run_info.preview_size is not None and self.run_info.n_files is not None:
            return f"First {self.run_info.preview_size} entries from {self.run_info.n_files} files"
        elif self.run_info.n_files is not None:
            return f"First {self.run_info.n_files} files"
        elif self.run_info.preview_size is not None:
            return f"First {self.run_info.preview_size} entries from all files"
        else:
            return "Complete dataset"

    def __get_cache_path(self):
        if self.runManConfig["CACHE_PATH"] == "":
            return os.path.join(
                "cache", Path(__main__.__file__).stem
            )
        else: 
            return self.runManConfig["CACHE_PATH"]

    def __get_cache_filePath(self, tag=""):
        hash, dataSelection = self.run_info.getHash(tag)
        path = os.path.join(
            self.__get_cache_path(),
            f"""{self.run_name}_{tag}_{hash}.pkl"""
        )
        return path, hash

    def __get_cache_info_filePath(self):
        cacheInfoPath = os.path.join(
            self.__get_cache_path(),
            self.run_name.replace("/", "") + "_info.yaml"
        )
        return cacheInfoPath

    def __to_cache(self):
        cache_path = self.__get_cache_path()
        if not os.path.exists(cache_path):
            os.mkdir(cache_path)

        if(self.run_info.DAQ_active and self.daq is not None):
            daq_file, runInfoHash = self.__get_cache_filePath("DAQ")
            self.daq.to_pickle(daq_file)
        if(self.run_info.ECONT_active and self.econt is not None):
            econt_file, runInfoHash = self.__get_cache_filePath("ECONT")
            self.econt.to_pickle(econt_file)

        info = None
        try:
            file = self.__get_cache_info_filePath()
            with open(file, "r") as f:
                info = yaml.safe_load(f)
        except FileNotFoundError:
            info = {"DAQ":{},"ECONT":{}}
        with open(self.__get_cache_info_filePath(), "w") as f:

            if(self.run_info.DAQ_active and self.daq is not None):
                hash, hashSelection = self.run_info.getHash("DAQ")
                info["DAQ"][hash] = hashSelection
            if(self.run_info.ECONT_active and self.econt is not None):
                hash, hashSelection = self.run_info.getHash("ECONT")
                info["ECONT"][hash] = hashSelection

            yaml.dump(info, f)

    def __load_from_cache(self, tag):
        try:
            cacheFilePath, hash = self.__get_cache_filePath(tag)
            data = pd.read_pickle(cacheFilePath)
            print(f"loaded {tag}-df from cache: {hash}")
            return data, True
        except FileNotFoundError:
            return None, False
    
    # def __update_PreCutString(self, trigtimeCut, thresholdCut, calibrationChannelCut):
    #     # apply optional calibration channel pre-cut
    #     #if self.run_info[]
    #     if(calibrationChannelCut):
    #         if len(self.run_info["pre_cut_string"]) > 3:
    #             self.run_info["pre_cut_string"] += " & (channel >= 0) & (channel <= 35)"
    #         else:
    #             self.run_info["pre_cut_string"] = "(channel >= 0) & (channel <= 35)"
    #     # find new precut elements depending on trigtimeCut and thresholdCut
    #     if (trigtimeCut or thresholdCut) and self.runconfig is not None :
    #         precutMods = []
    #         for conf in self.runconfig["_configs"]:
    #             precutMod = f"""(chip == {conf["chip"]}) & (half == {conf["half"]})"""
    #             if trigtimeCut:
    #                 precutMod += f""" & (trigtime >= {conf["trigtimecut_low"]}) & (trigtime < {conf["trigtimecut_high"]})"""
    #             if thresholdCut:
    #                 precutMod += f""" & (adc >= {conf["adcthreshold"]})"""
    #             precutMods.append(precutMod)
    #         # modify the pre_cut
    #         if len(self.run_info["pre_cut_string"]) > 3: self.run_info["pre_cut_string"]+= " & "
    #         modifiedPreCut = ""
    #         for precutMod in precutMods:
    #             if len(modifiedPreCut) > 3: modifiedPreCut+= " | "
    #             modifiedPreCut+=( self.run_info["pre_cut_string"] + precutMod)
    #         self.run_info["pre_cut_string"] = modifiedPreCut

    # run after loading a dataset
    def get_runconfig(self):
        # Read runconfig YAML file
        DatasetConf = None
        try:
            with open('config/dataset_config.yaml', 'r') as stream:
                DatasetConf = yaml.safe_load(stream)
        except Exception as e:
            DatasetConf = None
            print("dataset_config.yaml not loaded: " + str(e))
            return None
        # get matching config
        thisDatasetConfigs = []
        if DatasetConf:
            if 'datasets' in DatasetConf:
                thisDatasetConfigs = [config for config in DatasetConf['datasets'] if config["_run"] == self.run_name]
        if len(thisDatasetConfigs) > 1: print(f"""WARNING: more than one config found for run: {self.run_name}""")
        elif len(thisDatasetConfigs) == 0: 
            print(f"""no config found for run: {self.run_name}""")
            return None
        if self.daq is not None: thisDatasetConfigs[0]["_configs"] = filterConfigElements(thisDatasetConfigs[0]["_configs"], self.daq)
        return thisDatasetConfigs[0]