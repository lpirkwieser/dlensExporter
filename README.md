# dlensExporter
Python GUI program to convert .dlens files from Delver Lens N mobile application into .csv format to allow importing into various sites and platforms. 

<p align="center">
  <img src="demo.gif" alt="Demo" />
</p>

## Usage

You need three files:

* data.db from /res/raw/ in Delver Lens N APK, you can obtain this by extracting the APK downloadable for example from https://apkcombo.com/mtg-card-scanner-delver-lens/delverlab.delverlens/.
* .json file with offline card data from Scryfall, downloadable from https://scryfall.com/docs/api/bulk-data, Default Cards should suffice for most cases.
* .dlens file from Delver Lens N through it's backup or export deck option.

Clone the repository and install necessary dependecies. Under releases I have included pre-compiled binaries but due to included dependencies they're quite large.
    
## Notes

* Currently only supports Deckbox .csv format. There are some differences between what Scryfall API provides as card or set names, and some of these are automatically converted. I have added some I've come across myself, but it's not all-inclusive.

## Cli Usage
Store the above mentioned data.db and scryfall json files into the externalres subfolder as data.db and scryfall.json respectively. 

Now you can convert your .dlens file like this:
```
python dlense_convert.py "myexport.dlens"
```
The converted file will be placed in the output folder.
By default the script will export your .dlens file as a text file each line representing a card and its quantity. E.g.
```
12 Plain
10 Swamp
1 Generous Gift
1 Sol Ring
...
```
This format should be accepted by most websites like moxfield to share your decklist.

If you want to get the same .csv file format that the GUI script exports add the `--csv` flag.  