import os,sys
import yaml
import json
import requests
from yaml.loader import SafeLoader

def get_abs_filepath(filepath):
    """
    get absolute filepath for the given relative path
    """
    return os.path.join(os.getcwd(),filepath)

def json_load(filename="config.json"):
    """
    read given json file into dict and return
    """
    config = None
    try:
        with open(filename) as fobj:
            config = json.load(fobj)
            count = len(config)
    except (OSError, json.decoder.JSONDecodeError):
        print(
            "config file missing or incorrect, please provide following configurations..."
        )
    finally:
        return config
    
def yaml_loader(filepath):
    """ 
    Read yaml file and return the dict
    """
    # logging.info("Reading script yml file")
    data = dict()
    if os.path.isfile(filepath):
        with open(filepath, "r") as obj:
            data = yaml.load(obj, Loader=SafeLoader)
        if not data:
            return dict()
    else:
        print("invalid file {0}".format(filepath))
        sys.exit(0)
    return data

def yaml_dump(filepath, data):
    """
    Write the dict to yaml file
    """
    with open(filepath, "w") as obj:
        yaml.dump(data, obj, sort_keys=False, default_flow_style=False)

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