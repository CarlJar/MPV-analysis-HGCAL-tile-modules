import os, yaml

class AnalysisConfig:
    def __init__(self):
        self.base_path = os.path.dirname(__file__) + "/"
        self.config_path = self.base_path + "config/"
        with open(self.config_path + "analysis_config.yaml") as f:
            self.analysis_config = yaml.safe_load(f)

    def name(self, key):
        if key in self.analysis_config["columns"]:
            return self.analysis_config["columns"][key]["name"]
        else:
            return key

    def resolution(self, key):
        if key in self.analysis_config["columns"]:
            return self.analysis_config["columns"][key]["res_bit"]
        else:
            return 10

    def granularity(self, key):
        if key in self.analysis_config["columns"]:
            return self.analysis_config["columns"][key]["granularity"]
        else:
            return 1

    # def group(self, CalSC, key):
    #     return self.analysis_config["data_groups"][CalSC][key]

    # def setGranularity(self, key, value):
    #     self.analysis_config["columns"][key]["granularity"] = value


    # def histSettings(self):
    #     return self.analysis_config["hist_settings"]