import configparser


def build_config():
    config_parser = configparser.ConfigParser()
    try:
        config_parser.read("configs/config.ini")
        config = dict(config_parser["ASSET"])
        return config
    except:
        raise Exception('Improper configuation of configs/config.ini, see sample.congif.ini')
    return None