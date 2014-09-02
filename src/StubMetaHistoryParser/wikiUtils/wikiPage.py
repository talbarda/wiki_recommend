__author__ = 'talbarda'
import os
from wikiUtils.constants import NAMESPACES_DICT
from wikiUtils.utils import isEmpty
import xml.etree.ElementTree as ET


class wikiRevision(object):
    def __init__(self, revisionID, revisionTS, revisionUserName, revisionUserID, revisionTextBytes, revisionComment):
        self.revisionID = revisionID
        self.revisionTS = revisionTS
        self.revisionUserName = revisionUserName
        self.revisionUserID = revisionUserID
        self.revisionTextBytes = revisionTextBytes
        self.revisionComment = revisionComment

    def __hash__(self):
        return hash(self.revisionID)

    def __eq__(self, other):
        return type(self) == type(other) and \
               self.revisionID == other.revisionId and \
               self.revisionUserID == other.revisionUserID and \
               self.revisionTS == other.revisionTS

    @staticmethod
    def fromRevisionXMLElement(revisionXMLElement):
        contributorElement = revisionXMLElement.find('contributor')
        userName = contributorElement.find('username')
        userIP = contributorElement.find('ip')
        userID = contributorElement.find('id')
        textElement = revisionXMLElement.find('text')
        commentElement = revisionXMLElement.find('comment')
        return wikiRevision(revisionID=long(revisionXMLElement.find('id').text),
                            revisionTS=revisionXMLElement.find('timestamp').text,
                            revisionUserName=userName.text if not isEmpty(userName) else userIP.text if not isEmpty(
                                userIP) else None,
                            revisionUserID=long(userID.text) if not isEmpty(userID) else None,
                            revisionTextBytes=textElement.attrib['bytes'] if not isEmpty(
                                textElement) and 'bytes' in textElement.attrib else None,
                            revisionComment=commentElement.text if not isEmpty(
                                commentElement) and commentElement.text != '*' else None)


class wikiPage(object):
    def __init__(self, pageId, pageTitle, namespaceEnum, redirectTitle=None, revisions=None):
        self.pageID = pageId
        self.pageTitle = pageTitle.encode('utf8')
        self.ns = namespaceEnum
        self.redirectTitle = redirectTitle
        self.revisions = set() if isEmpty(revisions) else set(revisions)
        namespaceStr = NAMESPACES_DICT[self.ns]
        self.realPageTitle = \
            (redirectTitle if not isEmpty(redirectTitle) \
                else pageTitle.replace(namespaceStr, NAMESPACES_DICT[self.ns - 1]) if 'talk' in namespaceStr.lower() \
                else pageTitle).encode('utf8')

    def toCSVRows(self, colsDelim=',', rowsDelim=os.linesep):
        revisionsCounterPerUserID = {}
        for revision in self.revisions:
            if isEmpty(revision.revisionUserID):
                continue
            key = colsDelim.join([self.pageTitle, self.realPageTitle, str(self.pageID),str(revision.revisionUserID)])
            if key not in revisionsCounterPerUserID:
                revisionsCounterPerUserID[key] = 1
            else:
                revisionsCounterPerUserID[key] = revisionsCounterPerUserID[key] + 1

        return rowsDelim.join(colsDelim.join([revisionKey, str(revisionCount)]) for revisionKey, revisionCount in
                              revisionsCounterPerUserID.items())


    @staticmethod
    def fromPageXMLElement(pageXMLElementStringValue):
        pageElement = ET.fromstring(pageXMLElementStringValue)
        redirectElement = pageElement.find('redirect')

        revisions = []
        for revision in pageElement.findall('revision'):
            revisions.append(wikiRevision.fromRevisionXMLElement(revision))

        return wikiPage(pageId=long(pageElement.find('id').text),
                        pageTitle=pageElement.find('title').text,
                        namespaceEnum=int(pageElement.find('ns').text),
                        redirectTitle=redirectElement.attrib['title'] if not isEmpty(
                            redirectElement) and 'title' in redirectElement.attrib else None,
                        revisions=revisions)