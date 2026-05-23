import configparser
import os


class ConfigReader:
    _config = None

    @classmethod
    def _load(cls):
        # Cache config.ini after the first read so every step uses the same settings.
        if cls._config is None:
            config_path = os.path.join(os.getcwd(), "config.ini")
            cls._config = configparser.ConfigParser()
            cls._config.read(config_path)
        return cls._config

    @classmethod
    def get_base_url(cls):
        return cls._load().get("DEFAULT", "base_url")

    @classmethod
    def get_browser(cls):
        return cls._load().get("DEFAULT", "browser", fallback="edge")

    @classmethod
    def get_timeout(cls):
        return cls._load().getint("DEFAULT", "timeout", fallback=20)

    @classmethod
    def get_implicit_wait(cls):
        return cls._load().getint("DEFAULT", "implicit_wait", fallback=5)

    @classmethod
    def get_headless(cls):
        return cls._load().getboolean("DEFAULT", "headless", fallback=False)

    @classmethod
    def get_mobile(cls):
        return cls._load().get("DEFAULT", "mobile")
