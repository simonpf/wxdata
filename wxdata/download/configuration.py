import os
from configparser import ConfigParser
from appdirs import user_config_dir

"""
Dictionary holding known identities.
"""
identities = {}

"""
Path of the configuration file.
"""
identity_file = os.path.join(user_config_dir("wxdata", "simonpf"), "identities.ini")

################################################################################
# Handling identities
################################################################################

def parse_identity_file():
    """
    If available, parses identity config file and adds entries to known
    identities.
    """
    if os.path.exists(identity_file):
        config = ConfigParser()
        config.read(identity_file)
        for s in config.sections():
            identities[s] = dict([(k, config[s][k]) for k in config[s].keys()])
    else:
        print(f"No configuration file found in {identity_file}.")

def add_identity(domain, user, password):
    """
    Add identity to known identities.

    Args:
        domain(str): Name of the domain for which the identity
           is valid.
        user: User name for the identity
        password: Password for the identity
    """
    identities[domain] = {"user" : user,
                          "password" : password}

def get_identity(domain):
    """
    Retrieve identity for given domain.

    Args:
       domain(str): Name of the domain

    Returns:
       Dictionary containing keys 'username' and 'password'
       providing the authentication data for the given domain.

    Raises:
       Exception, if no identity for the given domain could be found.
    """
    if domain in identities:
        return identities[domain]
    else:
        raise Exception(f"Could not find identity for {domain}. Add section to "
                        " to configuration file {identity_file} or add an identity"
                        " manually using the 'add_identity' method.")

parse_identity_file()


