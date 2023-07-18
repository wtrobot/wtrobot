import os,sys
import yaml
import json
import requests
from yaml.loader import SafeLoader
from configparser import ConfigParser

class Utils:
    
    @staticmethod
    def check_file_exist(filepath):
        """
        Check if the given file exist
        """
        return os.path.isfile(filepath) 
    
    @staticmethod
    def get_abs_filepath(filepath):
        """
        get absolute filepath for the given relative path
        """
        return os.path.join(os.getcwd(),filepath)

    @staticmethod
    def json_load(filename="config.json"):
        """
        read given json file into dict and return
        """
        config = None
        try:
            if os.stat(filename).st_size != 0:
                with open(filename) as fobj:
                    # The json.load() is used to read the JSON document from file
                    config = json.load(fobj)
            else:
                # The json.loads() is used to convert the JSON String document into the Python dictionary
                config = json.loads("{}")
            
            count = len(config)
        except (OSError, json.decoder.JSONDecodeError):
            print(
                "config file missing or incorrect, please provide following configurations..."
            )
        finally:
            return config

    @staticmethod
    def json_dump(filename, data):
        with open(filename,"w") as fobj:
            json.dump(data,fobj,indent = 4)

    @staticmethod
    def change_yaml_file_extension(filepath):
        '''
        This function will change .yaml file extension to .yml and vic versa 
        '''
        _ , file_extension = os.path.splitext(filepath)
        ext = {".yml",".yaml"}
        file_ext = set(file_extension)
        updated_ext = list(ext - file_ext)[0] 
        return filepath.replace(file_extension, updated_ext)
    
    @staticmethod
    def yaml_loader(filepath):
        """ 
        Read yaml file and return the dict
        """
        # logging.info("Reading script yml file")
        data = dict()
        # print("1",filepath) 
        
        # check if given yaml file exist
        if os.path.isfile(filepath):
            with open(filepath, "r") as obj:
                data = yaml.load(obj, Loader=SafeLoader)

        # if in first pass file is not present then change the extension and again check the file existance
        elif not os.path.isfile(filepath):
            # if no .yaml file found change extension to .yml and check
            new_filepath = Utils.change_yaml_file_extension(filepath) 
            if os.path.isfile(new_filepath):
                with open(new_filepath, "r") as obj:
                    data = yaml.load(obj, Loader=SafeLoader)
            
            # print("2",filepath)  
        
        else:
            print("invalid file {0}".format(filepath))    
            sys.exit(0)
        
        return data

    @staticmethod
    def yaml_dump(filepath, data):
        """
        Write the dict to yaml file
        """
        with open(filepath, "w") as obj:
            yaml.dump(data, obj, sort_keys=False, default_flow_style=False)

    @staticmethod
    def read_ini_file(filepath):
        """
        read config/ini file and return config object
        """
        config = False
        if os.path.isfile(filepath):
            config = ConfigParser()
            config.read(filepath)
        return config

    @staticmethod
    def check_url(url):
            """
            This function is used to check if the given link is broken or not.It simply makes a http call and checks response
            :input url: link which you want to check
            :return: True if response is 200 else False
            """
            try:
                if "file:" in url:
                    return True
                else:
                    request = requests.get(url, verify=False)
                    if request.status_code == 200:
                        return True
                    else:
                        return False
            except Exception as e:
                print(e)
                return False