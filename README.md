#DJ's Metal Arms Tools#

##mst\_insert.py##
mst\_insert.py allows you to insert a file into any MST and replace a file with the exact same name. So for example if you make a modification to we01multi01.wld (the world file for Big E's House), you can use this tool to insert it into the MST so you can test it out in game!

##wld\_extractor.py##
wld\_extractor.py takes input of a wld files extracted using amPerl's MST extractor(https://github.com/amPerl/MATools) and splits it into (mostly) editable parts. You can then rebuild it and plug it right back into the MST!

##Usage##

###mst\_insert.py###
```
usage: mst_insert.py [-h] [-g | -x] input mst

Insert a file into the MST

positional arguments:
  input           File to insert into the mst
  mst             The MST

optional arguments:
  -h, --help      show this help message and exit
  -g, --gamecube  Use gamecube endian - big endian
  -x, --xbox      Use xbox endian - big endian [Default]
```


###wld\_extractor.py###
```
usage: wld_extractor.py [-h] [-g | -x] [-e | -r] [-p] input output

Extract or rebuild a wld file

positional arguments:
  input           input file or folder
  output          output file or folder

optional arguments:
  -h, --help      show this help message and exit
  -g, --gamecube  Use gamecube endian - big endian
  -x, --xbox      Use xbox endian - big endian [Default]
  -e, --extract   Extract the contents of a wld file to a directory
  -r, --rebuild   Rebuild a wld file from a folder full of extracted files
  -p, --print     Print the structures to stdout

```
