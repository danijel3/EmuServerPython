import base64
import importlib
from abc import abstractmethod

from Settings import get_setting


class EmuSource:
    @abstractmethod
    def do_login(self):
        """Check if Source requires login

        :return: boolean True/False value
        """
        pass

    @abstractmethod
    def check_user(self, user):
        """Check if username is correct
        Note: this method is not really recommended for security, but is still present as a feature.

        :param user: username to check
        :return: boolean True/False
        """
        pass

    @abstractmethod
    def check_login(self, user, passwd):
        """Check login given username and password

        :param user: username to check
        :param passwd: password to check
        :return: boolean True/False
        """
        pass

    @abstractmethod
    def get_config(self):
        """Get the main source configuration JSON

        :return: configuration as a JSON string.
        """
        pass

    @abstractmethod
    def save_config(self, data):
        """ Save the configuration

        :param data: configuration as a JSON string
        """
        pass

    @abstractmethod
    def get_bundle_list(self):
        """Get a list of bundles in a JSON list

        :return: JSON string
        """
        pass

    @abstractmethod
    def get_bundle(self, session, bundle):
        """Get a bundle as a JSON stirng

        :param session: session of the bundle
        :param bundle: name of the bundle
        :return: JSON string
        """
        pass

    @abstractmethod
    def save_bundle(self, session, bundle, data):
        """Save a bundle

        :param session: session of the bundle
        :param bundle: name of the bundle
        :param data: modified JSON string
        """
        pass

    @staticmethod
    def get_file(path, base64_enc=False):
        if base64_enc:
            with open(path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        else:
            with open(path, 'r') as f:
                return f.read()

    @staticmethod
    def save_file(path, data, base64_dec=False):
        if base64_dec:
            with open(path, 'wb') as f:
                f.write(base64.b64decode(data))
        else:
            with open(path, 'w') as f:
                f.write(data)


def get_source(path):
    if not get_setting('source', 'type'):
        return None
    source_type = get_setting('source', 'type')
    m = importlib.import_module(f'sources.{source_type}')
    c = getattr(m, source_type)
    return c(path)
