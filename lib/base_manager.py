import json
import os
import copy

class UtilityMixin:
    ''' Util class providing utilities like getting base configurations. '''

    def __init__(self):
        self.config = {}

    @property
    def config_data(self):
        ''' 
        This is a getter property and
        config_data acts as a variable due to @property decorator.
        '''
        self.config = self.get_base_config()
        return copy.deepcopy(self.config)

    @config_data.setter
    def config_data(self, newConfig=None):
        ''' This is a setter property. You can understand its working from the engine.py module.'''
        config = self.config_data
        for conf in newConfig:
            config[conf] = newConfig[conf]

        self.set_base_config(config)

    @staticmethod
    def get_base_config():
        ''' 
        This function writes the config data to config.json.
        Static methods do not use self.
        '''

        with open("./config.json") as data_file:
            config = json.load(data_file)
        return config or {}

    @staticmethod
    def set_base_config(config):
        ''' 
        This function reads the config data from config.json.
        Static methods do not use self.
        '''
        with open("./config.json", "w") as data_file:
            json.dump(config, data_file, indent=4, separators=(",", ": "))
        return True
