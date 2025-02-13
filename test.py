import logging.config
import os
import requests
import logging

from logging.config import dictConfig

from origin import Plugin_OBJ

class Mock_Logger():
    
    def __init__(self):
        logging_config = {
            'version': 1,
            'formatters': {
                'fHDHR': {
                    'format': '%(levelname)s - %(message)s'
                    },
            },
            'loggers': {
                # all purpose, fHDHR root logger
                'fHDHR': {
                    'level': 'DEBUG',
                    'handlers': ['console'],
                },
            },
            'handlers': {
                # output on stderr
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'fHDHR',
                }
            },
        }

        dictConfig(logging_config)
        self._logger = logging.getLogger('fHDHR')
        self.name = "IPTVorg"
        self.namespace = self.name.lower()

    def critical(self, message, *args, **kws):
        return self._logger.critical("[%s] %s" % (self.namespace, message), *args, **kws)

    def error(self, message, *args, **kws):
        return self._logger.error("[%s] %s" % (self.namespace, message), *args, **kws)

    def warning(self, message, *args, **kws):
        return self._logger.warning("[%s] %s" % (self.namespace, message), *args, **kws)

    def info(self, message, *args, **kws):
        return self._logger.info("[%s] %s" % (self.namespace, message), *args, **kws)

    def debug(self, message, *args, **kws):
        return self._logger.debug("[%s] %s" % (self.namespace, message), *args, **kws)
        

class Mock_Plugin_Config():
    
    def __init__(self):
        self._config = {"iptvorg": {"filter_country": ["CA"], "filter_languages": ["fra"], "filter_category": None}}
       
    @property
    def dict(self):
        return self._config.copy()
    
    def __getattr__(self, name):
        """
        Quick and dirty shortcuts. Will only get called for undefined attributes.
        """

        if checkattr(self._config, name):
            return eval("self._config.%s" % name)
        
def checkattr(inst_obj, attrcheck):

    # Quick check of hasattr
    if hasattr(inst_obj, attrcheck):
        return True

    # Check if attribute is in dir list
    if attrcheck in [x for x in dir(inst_obj) if not x.startswith("__")]:
        return True

    return False

class Mock_Web_Session():  
    
    @property 
    def session(self):
        return requests     
        

class Mock_Plugin_Utils():
    """
    A mock object to run the plugin outside of the application context.
    """

    def __init__(self):
        self.config = Mock_Plugin_Config()
        self.logger = Mock_Logger()
        self.web = Mock_Web_Session()
        
plugin = Plugin_OBJ(Mock_Plugin_Utils())
channels = plugin.get_channels()
