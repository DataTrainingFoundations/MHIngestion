import yaml

APP_CONFIG_FILENAME = 'app_config.yaml'

class AppConfig:
    _instance = None
    _data = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
            with open(APP_CONFIG_FILENAME, 'r') as file:
                cls._instance._data = yaml.safe_load(file)
        return cls._instance
        
    def __getitem__(self, key):
        return self._data[key]

if __name__ == "__main__":
    print(AppConfig()['database']['connection']['host'])
