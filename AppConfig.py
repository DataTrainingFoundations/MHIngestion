import yaml

APP_CONFIG_FILENAME = 'app_config.yaml'

class AppConfig:
    _instance = None
    _data = None

    def __init__(self):
        with open(APP_CONFIG_FILENAME,'r') as file:
            self._data = yaml.safe_load(file)
    
    def getAttribute(self, attribute:str) -> str:
        return self._data[attribute]
    
    def __getitem__(self, key):
        return self._data[key]
    

if __name__ == "__main__":
    appConfig : AppConfig = AppConfig()
    print(appConfig['database']['connection']['host'])

