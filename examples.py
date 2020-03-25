#!/usr/bin/python3

import covidKeralaDHS as co

# Example 1: Download pdf bulletin for a specific date
# bulletin 
print('Example 1')
co.getBulletin('23.03.2020')

# Example 2: Check for updated bulletins for a specific date and download it
print('Example 2')
isNew = co.isNewBulletin('24.03.2020')

if isNew:
    print('NEW BULLETIN AVAILABLE')
    # isNew will contain url of pdf bulletin
    co.downloadPDF(isNew)
    print('Downloaded to ' + co.bulletinDefaultFile)
else:
    print('NO NEW BULLETINS AVAILABLE')
