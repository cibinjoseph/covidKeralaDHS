"""
A module to parse the COVID bulletins provided by DHS Kerala
"""

import urllib3
from bs4 import BeautifulSoup
import json
import sys

linkPre = 'http://dhs.kerala.gov.in'
jsonDefaultFile = 'bulletinLinks.json'
bulletinDefaultFile = 'bulletin.pdf'

def __getPDFlink(bulletinPageLink):
    """
    Return links to pdf bulletin uploads in page.
    This link can be checked for updated bulletins.
    """
    # Parse bulletin page to get pdf link
    req = urllib3.PoolManager()
    bulletinPage = req.request('GET', bulletinPageLink)
    soup = BeautifulSoup(bulletinPage.data, 'html.parser')
    try:
        divTag = soup.find('div', attrs={'class': 'entry-content'})
        pTags = divTag.findAll('p')
    except AttributeError:
        print('Error: Broken Connection. Rerun')
        raise ConnectionError

    # Get link to pdf bulletin
    for tag in pTags:
        if 'English' in tag.text:
            return linkPre + tag.a.get('href')
        else:
            return None

def cleanDate(date):
    """
    Returns the date in the format dd.mm.yyyy
    This can be used to write to the JSON file in a standard format
    """
    # Sanity checks
    if not isinstance(date,str):
        raise TypeError
    if not len(date) == 10:
        raise ValueError

    return date[0:2] + '.' + date[3:5] + '.' + date[6:10]

def __getDateLinkDict(verbose=True):
    """
    Returns a dict data type containing all dates
    and their corresponding links to bulletin pages.
    """
    # Ensure python version 3+
    if sys.version < (3, 0):
        print('ERROR: Use python version 3+')
        raise SyntaxError

    # Parse DHS Kerala webpage to get html tags
    if verbose:
        print('Parsing Kerala DHS webpage ...')
        print('Obtaining links of dates:')
    DHSLink = linkPre + '/%e0%b4%a1%e0%b5%86%e0%b4%af%e0%b4%bf%e0%b4%b2%e0%b4%bf-%e0%b4%ac%e0%b5%81%e0%b4%b3%e0%b5%8d%e0%b4%b3%e0%b4%b1%e0%b5%8d%e0%b4%b1%e0%b4%bf%e0%b4%a8%e0%b5%8d%e2%80%8d/'
    req = urllib3.PoolManager()
    DHSPage = req.request('GET', DHSLink)
    soup = BeautifulSoup(DHSPage.data, 'html.parser')
    tags = soup.findAll('h3', attrs={'class': 'entry-title'})

    # Clean html tags to extract date and corresponding link to pdfs bulletins
    dateLinkDict = dict()
    for tag in tags:
        # The returned dates may not be consistently formatted on the website.
        # Eg. dd-mm-yyy and dd/mm/yyyy are both found
        date = cleanDate(tag.a.text)
        bulletinPageLink = linkPre + tag.a.get('href')
        dateLinkDict[date] = __getPDFlink(bulletinPageLink)
        if verbose:
            print(date)

    return dateLinkDict

def downloadPDF(PDFlink):
    """
    Downloads pdf bulletin from the provided link
    """
    try:
        req = urllib3.PoolManager()
        response = req.request('GET', PDFlink)
        bulletinFile = open(bulletinDefaultFile, 'wb')
        bulletinFile.write(response.data)
    except HTTPError:
        print('Error: PDF file not found')
        return False
    finally:
        bulletinFile.close()

def writeJSON(dateLinkDict, filename=jsonDefaultFile):
    """
    Writes dateLinkDict as a json file.
    This JSON file can be used to check for updates.
    """
    jsonFile = open(filename, 'w')
    json.dump(dateLinkDict, jsonFile)
    jsonFile.close()

def readJSON(filename=jsonDefaultFile):
    """
    Reads all dateLinkDict from a json file.
    This JSON file can be used to check for updates.
    """
    jsonFile = open(filename, 'r')
    dateLinkDict = json.load(jsonFile)
    jsonFile.close()

    return dateLinkDict

def getBulletin(date, verbose=True):
    """
    Downloads latest bulletin for the given date and returns True.
    Returns False if bulletin is not available.
    """
    stdDate = cleanDate(date)
    dateLinkDict = __getDateLinkDict(verbose)
    if stdDate in dateLinkDict:
        downloadPDF(dateLinkDict[stdDate])
        return True
    else:
        return False


def isNewBulletin(date, updateJSONfile=True, verbose=True):
    """
    Returns bulletin link if an updated bulletin is available on provided date.
    Returns False if no new bulletins are available.
    If running for first time, the JSON file is created and returns True.
    """
    stdDate = cleanDate(date)
    dateLinkDictNew = __getDateLinkDict(verbose)
    # If date does not exist on server
    if not stdDate in dateLinkDictNew:
        return False

    try:
        # If local JSON file exists in directory
        dateLinkDictOld = readJSON(jsonDefaultFile)
        # If date does not exist in local JSON file
        if not stdDate in dateLinkDictOld:
            if updateJSONfile:
                writeJSON(dateLinkDictNew)
            return True
        # If both bulletins are same
        if (dateLinkDictNew[stdDate] == dateLinkDictOld[stdDate]):
            return False
        else:
        # If both bulletins are different
            if updateJSONfile:
                writeJSON(dateLinkDictNew)
            return True
    except FileNotFoundError:
        # If local JSON file does not exist
        if updateJSONfile:
            writeJSON(dateLinkDictNew)
        return True


if __name__ == "__main__":
    """
    If the module is invoked as a python program, it checks for new bulletins
    and downloads the latest one.
    """
    from datetime import date
    today = date.today().strftime('%d.%m.%Y')
    isNew = isNewBulletin(today)
    if isNew:
        print('NEW BULLETIN AVAILABLE')
        downloadPDF(isNew)
        print('Downloaded to ' + bulletinDefaultFile)
    else:
        print('NO NEW BULLETINS AVAILABLE')
