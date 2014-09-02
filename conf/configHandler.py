__author__ = 'talbarda'
import ConfigParser

from Utils import Constants


class configHandler(object):
    def __init__(self, configFileName=None):
        self.config = ConfigParser.ConfigParser()
        self.readConfig(configFileName)

    def readConfig(self, configFileName):
        self.config.read([configFileName])

    def getParamVal(self, paramFullName, paramType=str, defParamValue=None):
        paramFullNameLower = paramFullName
        paramParts = paramFullNameLower.split(Constants.CONF_CATEG_PARAM_NAME_DELIM)

        # # Checking if the param asked is the "param_name" format that means it is in the general parameters
        # # or in "Section.param_name" format"
        if len(paramParts) == 1:
            paramSection = Constants.GENERAL_CONF_SECTION_NAME
        else:
            paramSection = paramParts[0]

        paramName = paramParts[len(paramParts) - 1]

        try:
            if paramType is str:
                paramValue = self.config.get(paramSection, paramName)
            elif paramType is int:
                paramValue = self.config.getint(paramSection, paramName)
            elif paramType is float:
                paramValue = self.config.getfloat(paramSection, paramName)
            elif paramType is bool:
                paramValue = self.config.getboolean(paramSection, paramName)

            return paramValue
        except ConfigParser.NoSectionError:
            return defParamValue
        except ConfigParser.NoOptionError:
            return defParamValue