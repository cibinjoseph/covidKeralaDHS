# covidKeralaDHS
Python module to parse Kerala DHS website for daily bulletins on COVID cases

## Usage
Example 1: Download pdf bulletin for a specific date  
```
import covidKeralaDHS as co
co.getBulletin('23.03.2020')
```  

Example 2. Check for updated bulletins for a date
```
import covidKeralaDHS as co
isNew = co.isNewBulletin('24.03.2020')
if isNew:
  print('NEW BULLETIN DOWNLOADED')
else:
  print('NO UPDATES')
```

## Documentation
For a list of available functions, import the module and use help():
```
import covidKeralaDHS as co
help(co)
```
