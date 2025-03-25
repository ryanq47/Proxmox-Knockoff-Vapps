class ConfigSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConfigSingleton, cls).__new__(cls)
            cls._instance.values = {}
        return cls._instance

    def set_value(self, key, value):
        self.values[key] = value

    def get_value(self, key, default=None):
        return self.values.get(key, default)


# # Usage Example:
# if __name__ == "__main__":
#     config1 = ConfigSingleton()
#     config1.set_value("proxmox_url", "https://10.0.0.2:8006")

#     config2 = ConfigSingleton()
#     print(config2.get_value("proxmox_url"))  # This will print: https://10.0.0.2:8006

#     # Both config1 and config2 refer to the same instance
#     print(config1 is config2)  # True
