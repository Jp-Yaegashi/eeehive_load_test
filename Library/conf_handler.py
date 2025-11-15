
from Library.debug import logging
import configparser
config = configparser.ConfigParser()

class conf_handler:
    def __init__(self, file):
        # メンバ変数
        self.__file = file

    def get(self, section, key):
        config.read(self.__file)
        return config.get(section, key)
    
    def getboolean(self, section, key):
        config.read(self.__file)
        return config.getboolean(section, key)
    
    def set(self, section, key, value):
        config.read(self.__file)
        config[section][key] = value
        with open(self.__file, 'w') as configfile:
            config.write(configfile)
