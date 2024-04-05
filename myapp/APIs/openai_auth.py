import os
from os.path import expanduser
import json
class OpenAIApi():
    CONFIG_NAME_PATH = 'path'
    CONFIG_NAME_ORGANIZATION = 'organization'
    CONFIG_NAME_KEY = 'key'

    config_dir = os.environ.get('OPENAI_CONFIG_DIR') or os.path.join(
        expanduser('~'), '.openai')
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    config_file = 'openai.json'
    config = os.path.join(config_dir, config_file)
    config_values = {}
    already_printed_version_warning = False

    def authenticate(self):
        config_data = {}

        # Step 1: try getting username/password from environment
        config_data = self.read_config_environment(config_data)

        # Step 2: if credentials were not in env read in configuration file
        if self.CONFIG_NAME_ORGANIZATION not in config_data \
                or self.CONFIG_NAME_KEY not in config_data:
            if os.path.exists(self.config):
                config_data = self.read_config_file(config_data)
            else:
                raise IOError('Could not find {}. Make sure it\'s located in'
                                ' {}. Or use the environment method.'.format(
                                    self.config_file, self.config_dir))

        # Step 3: load into configuration!
        self.CONFIG_NAME_ORGANIZATION = config_data["organization"]
        self.CONFIG_NAME_KEY = config_data["api_key"]

    def read_config_environment(self, config_data=None, quiet=False):
        if config_data is None:
            config_data = {}
        for key, val in os.environ.items():
            if key.startswith('OPENAI_'):
                config_key = key.replace('OPENAI_', '', 1).lower()
                config_data[config_key] = val

        return config_data
    
    def read_config_file(self, config_data=None, quiet=False):
        if config_data is None:
            config_data = {}

        if os.path.exists(self.config):
            try:
                if os.name != 'nt':
                    permissions = os.stat(self.config).st_mode
                    if (permissions & 4) or (permissions & 32):
                        print(
                            'Warning: Your OPENAI API key is readable by other '
                            'users on this system! To fix this, you can run ' +
                            '\'chmod 600 {}\''.format(self.config))
                with open(self.config) as f:
                    config_data = json.load(f)
            except:
                pass
        else:

            # Warn the user that configuration will be reliant on environment
            if not quiet:
                print('No OPENAI API config file found, will use environment.')

        return config_data
