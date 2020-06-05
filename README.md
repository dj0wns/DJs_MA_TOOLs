# DJ's Metal Arms Tools #

## Getting Started ##
1. Clone the repository with `git clone https://github.com/dj0wns/DJs_MA_TOOLs`
2. Install Python3.7 or newer if you don't already have Python: [Python](https://www.python.org/downloads/)
3. Run `pip install -r requirements.txt` to install all dependencies
4. Start modding!

## visual\_wld\_editor.py ##
Adding, removing and editting shapes is a breeze with this hot new wld editor. Fully featured and supporting a variety of maps(More to be added over time). This script has a full gui and allows for fairly accurate placement of shapes as well as complete control over all of their attributes.

## mst\_extract.py ##
mst\_extract.py extracts all files in the MST to the provided folder. This is how you get files to modify with the other scripts.

## mst\_insert.py ##
mst\_insert.py allows you to insert a file into any MST and replace a file with the exact same name. This is how you put your modded files back into the game!

## wld\_extractor.py ##
wld\_extractor.py takes input of a wld files extracted mst\_extract.py and splits it into (mostly) editable parts. You can then rebuild it and plug it right back into the MST!

## csv\_extractor.py ##
csv\_rebuilder.py takes input of a csv file extracted with mst\_extract.py and rebuilds it so it can be reinserted into the MST.

## sma\_extractor.py ##
sma\_extractor.py takes input of a sma file extracted with mst\_extract.py and outputs an assembly like representation. After editing, sma\_extractor.py can rebuild this script into a valid sma script that can be inserted into the MST.

## Usage ##

### mst\_extract.py ###
```
usage: mst_extract.py [-h] [--ignore-existing] [-f FILE] mst path

positional arguments:
  mst                   path to the Metal Arms .MST file
  path                  directory to put the extracted files in

optional arguments:
  -h, --help            show this help message and exit
  --ignore-existing
  -f FILE, --file FILE  extract only specific file
```


### mst\_insert.py ###
```
usage: mst_insert.py [-h] [-g | -x] [-s SUFFIX] mst files [files ...]

Insert a file into the MST

positional arguments:
  mst                   The MST
  files                 Files to insert into the mst

optional arguments:
  -h, --help            show this help message and exit
  -g, --gamecube        Use gamecube endian - small endian
  -x, --xbox            Use xbox endian - big endian [Default]
  -s SUFFIX, --suffix SUFFIX
                        The suffix for the new mst. Is '.new' by default. If
                        this is blank it will overwrite the mst.
```


### wld\_extractor.py ###
```
usage: wld_extractor.py [-h] [-g | -x] [-e | -r | -i] [-p] input output

Extract or rebuild a wld file

positional arguments:
  input           input file or folder
  output          output file or folder

optional arguments:
  -h, --help      show this help message and exit
  -g, --gamecube  Use gamecube endian - small endian
  -x, --xbox      Use xbox endian - big endian [Default]
  -e, --extract   Extract the contents of a wld file to a directory
  -r, --rebuild   Rebuild a wld file from a folder full of extracted files
  -i, --insert    Inserts a folder full of shapes into the wld, overwriting
                  the current shapes, put the .wld file as input and a folder
                  containing shapes as output
  -p, --print     Print the structures to stdout
```

### csv\_rebuilder.py ###
```
usage: csv_rebuilder.py [-h] [-g | -x] input output

Rebuild a CSV file

positional arguments:
  input           Input CSV file
  output          Output file

optional arguments:
  -h, --help      show this help message and exit
  -g, --gamecube  Use gamecube endian - small endian
  -x, --xbox      Use xbox endian - big endian [Default]
```


### sma\_extractor.py ###

EXPERIMENTAL - currently only works on Linux and changing the count of instructions is likely to break. Good luck!

```
usage: sma_extractor.py [-h] [-e | -r] [-p] input output

Extract or rebuild a sma file

positional arguments:
  input          input file or folder
  output         output file or folder

optional arguments:
  -h, --help     show this help message and exit
  -e, --extract  Extract the contents of a sma file to a directory
  -r, --rebuild  Rebuild a sma file from a folder full of extracted files
  -p, --print    Print the structures to stdout
```
