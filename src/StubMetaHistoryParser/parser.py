import sys
from wikiUtils.utils import getListOfFilesToExtractFromDirectory, executeFunctionInParallel, getExceptionDetailedMessage

__author__ = 'talbarda'

import os
from wikiUtils.wikiPage import wikiPage

COLS_DELIM = ',WR_CL_DL,'
CSV_HEADLINE = COLS_DELIM.join(['TITLE', 'REAL_TITLE', 'ID', 'USER_ID', 'NUM_REVISIONS'])

def printMsg(msg):
    sys.stdout.write('%s%s' % (msg, os.linesep))
    sys.stdout.flush()

def proccessFile(stubMetaHistoryXMLFilePath):
    printMsg("Working on file \"%s\" size %d KB" % (stubMetaHistoryXMLFilePath, os.path.getsize(stubMetaHistoryXMLFilePath)))
    wikiEditHistoryXML = open(stubMetaHistoryXMLFilePath)
    wikiEditHistoryCSV = open(stubMetaHistoryXMLFilePath.replace('xml', 'csv'), 'w')
    numLinesRead = 0
    numPagesParsed = 0
    try:
        wikiEditHistoryCSV.write(CSV_HEADLINE)
        pageLines = []
        pageStarted = False
        for line in wikiEditHistoryXML:
            numLinesRead = numLinesRead + 1
            if line.strip() == '<page>':
                pageStarted = True
                pageLines.append(line)
            elif pageStarted:
                pageLines.append(line)
                if line.strip() == '</page>':
                    pageStarted = False
                    page = wikiPage.fromPageXMLElement(''.join(pageLines))
                    wikiEditHistoryCSV.write(
                        '%s%s' % (os.linesep, page.toCSVRows(colsDelim=COLS_DELIM)))
                    numPagesParsed = numPagesParsed + 1
                    pageLines = []

        printMsg("%d pages were found in %d lines in \"%s\" file" % (numPagesParsed, numLinesRead, stubMetaHistoryXMLFilePath))
        wikiEditHistoryCSV.flush()
    except:
        printMsg("Working on file \"%s\" failed.So far %d pages were found in %d lines.Error:%s%s" %
                 (stubMetaHistoryXMLFilePath, numPagesParsed, numLinesRead, os.linesep, getExceptionDetailedMessage()))
        wikiEditHistoryXML.close()
        wikiEditHistoryCSV.close()


def main():
    dirPath = '/Volumes/TalMyPassportForMac/WikiPedia/'
    wikiFiles = sorted(getListOfFilesToExtractFromDirectory(directoryPath=dirPath,
                                                            isRecursive=False,
                                                            suffixIncludingTheDot='.xml'),
                       key=lambda f: os.path.getsize(f))
    executeFunctionInParallel(funcName=proccessFile,
                              inputsList=wikiFiles,
                              maxParallelism=2)


if __name__ == "__main__":
    main()