import os

class ConfigReader:
    _config = {}

    @classmethod
    def load_config(cls):
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "config",
            "config.properties"
        )

        with open(config_path) as configfile:
            for line in configfile:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    cls._config[key.strip()] = value.strip()

        return cls._config

    @classmethod
    def get(cls, key):
        return cls.load_config().get(key)

    # Explicit getters
    @classmethod
    def get_base_url(cls):
        return cls.get("base_url")

    @classmethod
    def get_browser(cls):
        return cls.get("browser")

    @classmethod
    def get_implicit_wait(cls):
        return int(cls.get("implicit_wait"))

    @classmethod
    def get_timeout(cls):
        return int(cls.get("timeout"))

    @classmethod
    def get_headless(cls):
        return cls.get("headless").lower() == "true"