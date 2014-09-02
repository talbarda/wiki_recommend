__author__ = u'talbarda'

import os
import sys

from wikiUtils.constants import *


def getTagValue(searchableObject, tagName, tagType=str, defValue=None):
    tagValue = searchableObject.find(tagName)
    if isEmpty(tagValue):
        tagValue = defValue
    else:
        tagValue = tagType(tagValue.text)

    return tagName


def stringIsNumber(numberAsString):
    return STRING_IS_NUMBER_REGEX.match(numberAsString) is not None


def isIterable(obj):
    return hasattr(obj, '__iter__')


def isEmpty(obj):
    return (obj is None or obj == "") and (not isIterable(obj) or len(obj) == 0) and obj != 0


import traceback


def getExceptionDetailedMessage():
    exceptionInfo = sys.exc_info()
    tracebackDetail = os.linesep.join([str(item) for item in traceback.extract_tb(exceptionInfo[2])])
    return os.linesep.join([str({'ErrType': exceptionInfo[0].__name__}),
                            str({'ErrMsg': str(exceptionInfo[1])}),
                            str({'TraceBack': tracebackDetail})])


def getProblematicKeysToEncode(dct, encoderFunc):
    problematicKeysToEncode = set()
    for k in dct:
        val = dct[k]
        try:
            encoderFunc(val)
        except:
            problematicKeysToEncode.add(k)

    return problematicKeysToEncode


import json


def toJSON(obj):
    return json.dumps(obj=obj,
                      default=unicode,
                      ensure_ascii=False,
                      indent=4,
                      sort_keys=True)


def writeAsJSON(logger, content, fileOutputPath,
                encodeWithoutProblematicKeysIfFailed=False):
    try:
        # encode first - create file later (so if the encoding fails it won't create redundant files)
        contentJSON = toJSON(obj=content).encode('utf8')
        logger.info("Writing %d bytes content to \"%s\" path" % (sys.getsizeof(contentJSON), fileOutputPath))
        createParentDirIfNotExists(childPath=fileOutputPath)
        jsonFile = open(fileOutputPath, 'w')
        jsonFile.write(contentJSON)
        jsonFile.close()
    except:
        problematicKeysToEncode = getProblematicKeysToEncode(content, toJSON)
        logger.exception("Encoding dictionary to json in path %s failed. Problematic keys are %s" % (
            fileOutputPath, str(problematicKeysToEncode)))
        if encodeWithoutProblematicKeysIfFailed:
            logger.info("Trying to encode without the problematic keys")
            dictionaryContentWithoutProblematicKeys = dict(
                [(key, content[key]) for key in content.keys() if
                 key not in problematicKeysToEncode])
            writeAsJSON(logger, dictionaryContentWithoutProblematicKeys, fileOutputPath, False)
        else:
            raise


# TODO : change to create dir instead of parent dir
def createParentDirIfNotExists(childPath, logger=None):
    parentDirectoryPath = os.path.dirname(childPath)
    if logger:
        logger.debug(u'Parent directory of (%s) is (%s)' % (childPath, parentDirectoryPath))
    if not os.path.exists(parentDirectoryPath):
        os.makedirs(parentDirectoryPath)
        if logger:
            logger.debug(u'Parent directory does not exist. Creating directory %s' % parentDirectoryPath)
    return True


def hexStringToNumber(hexString):
    '''
    Converts the hex string to number (long)
    :param hexString: The give hex string
    :return: The long number that the hex string is equal to
    '''
    return long(hexString, 16)


def xorHexStrings(hexStr1, hexStr2):
    '''
    Compute the xor of the two hex strings by converting them to LONGs and then XORing them.
    Returns a long
    :param hexStr1: First hex string
    :param hexStr2: Second hex string
    :return: The xor of the two hex string as a long number
    '''
    return hexStringToNumber(hexStr1) ^ hexStringToNumber(hexStr2)


def sumDigits(num):
    digitsSum = 0
    while num:
        digitsSum += num % 10
        num /= 10
    return digitsSum


from multiprocessing import Pool, cpu_count, Lock


def executeFunctionInParallel(funcName, inputsList, maxParallelism=cpu_count()):
    parallelismPool = Pool(processes=maxParallelism)
    executeBooleanResultsList = parallelismPool.map(funcName, inputsList)
    parallelismPool.close()
    # if all parallel executions executed well - the boolean results list should all be True
    return all(executeBooleanResultsList)


import fnmatch
from os import walk, listdir
from os.path import isfile, join


def getListOfFilesToExtractFromDirectory(directoryPath, isRecursive=True, suffixIncludingTheDot=u'',
                                         excludePathsWithString='', fileSizeInBytesGreaterThen=-1):
    listOfFiles = []
    filePFilterPattern = u'*' + suffixIncludingTheDot
    if (isRecursive):
        for (dirpath, dirnames, filenames) in walk(directoryPath):
            if not excludePathsWithString or excludePathsWithString not in dirpath:
                listOfFiles.extend(
                    [join(dirpath, filename) for filename in fnmatch.filter(filenames, filePFilterPattern) if
                     os.path.getsize(join(dirpath, filename)) > fileSizeInBytesGreaterThen])
    else:
        if not excludePathsWithString or excludePathsWithString not in directoryPath:
            listOfFiles = [join(directoryPath, f) for f in listdir(directoryPath) if
                           isfile(join(directoryPath, f)) and f.endswith(suffixIncludingTheDot) and
                           os.path.getsize(os.path.join(directoryPath, f)) > fileSizeInBytesGreaterThen and
                           (not excludePathsWithString or excludePathsWithString not in f)]
    return listOfFiles


import shutil, exceptions


def copyFile(sourceDestPaths):
    sourcePath, destPath = sourceDestPaths
    try:
        shutil.copy(sourcePath, destPath)
        return True
    except exceptions.EnvironmentError:
        return False


def createLargeDocSeperatedByDelimiter(docs, delim=u'\n'):
    return delim.join([str(doc) for doc in docs])


import datetime
from enum import Enum

STDOUT_LOCATION = u'STDOUT'
STDOUT = sys.stdout
LogLevel = Enum(u'DEBUG', u'INFO', u'WARNING', u'ERROR', u'CRITICAL', u'EXCEPTION')


class Logger(object):
    def __init__(self, lock=Lock(), obj=None, conf=None, objName=None):
        self.lock = lock
        self.minLogLevelIndex = DEF_MIN_LOG_LEVEL \
            if not conf \
            else conf.getParamVal(paramFullName=MIN_LOG_LEVEL_INDEX_CONF_PARAM_NAME,
                                  paramType=int,
                                  defParamValue=DEF_MIN_LOG_LEVEL)

        if not obj and objName:
            self._initNoObj(objName)
        else:
            objType = type(obj)
            self.objTypeName = objType.__name__
            logLocation = conf.getParamVal(paramFullName=LOGS_CONF_SECTION_NAME + '.' + self.objTypeName,
                                           defParamValue=STDOUT_LOCATION) if conf else STDOUT_LOCATION

            if logLocation == STDOUT_LOCATION:
                self.file = STDOUT
            else:
                directoryPath = os.path.dirname(self.fileName)
                if not os.path.exists(directoryPath):
                    os.makedirs(directoryPath)
                self.file = open(self.fileName, 'a')

    def _initNoObj(self, objName):
        self.objTypeName = objName
        self.file = STDOUT

    def stopLogging(self):
        if self.file and self.file != STDOUT:
            self.file.close()

    def debug(self, logMessage):
        self.log(LogLevel.DEBUG, logMessage)

    def info(self, logMessage):
        self.log(LogLevel.INFO, logMessage)

    def warn(self, logMessage):
        self.log(LogLevel.WARNING, logMessage)

    def error(self, logMessage):
        self.log(LogLevel.ERROR, logMessage)

    def critical(self, logMessage):
        self.log(LogLevel.CRITICAL, logMessage)

    def exception(self, logMessage):
        self.log(LogLevel.EXCEPTION,
                 os.linesep.join([logMessage, "Exception details:", getExceptionDetailedMessage()]))

    def log(self, logLevel, logMessage):
        try:
            if logLevel.index >= self.minLogLevelIndex:
                fullMessage = '%s pid:%d %s %s:%s%s' % (
                    str(datetime.datetime.now()), os.getpid(), self.objTypeName, logLevel, logMessage, os.linesep)
                with self.lock:
                    self.file.write(fullMessage)
                    self.file.flush()
        except:
            pass