import argparse
import datetime
from functools import lru_cache
import sys
import json
import sqlite3

class ExportContext:
  offlinescryfall = ""
  apkc = None
  dlensc = None

  def __init__(self, offlinescryfall, apkdb):
    self.offlinescryfall = offlinescryfall
    # Open apkdb SQLite file
    self.connectapkdatabase(apkdb)

  def getCards(self, dlens):
    # Open dlens SQLit files
    self.connectdlensdatabase(dlens)
    self.dlensc.execute('SELECT * from cards')
    return self.dlensc.fetchall()
  
  def convertToDecklist(self, dlens: str):
    #self.offlinescryfall = offlinescryfall
    # Get all cards from .dlens file
    #self.dlensc.execute('SELECT * from cards')
    cardstoimport = self.getCards(dlens)#self.dlensc.fetchall()

    # Set new .csv file name
    now = datetime.datetime.now()
    newfilename = "output/" + now.strftime("%d_%m_%Y-%H_%M_%S") + ".txt"
    exportCards = {}
    # For each card, match the id to the apk database and with scryfall_id search further data from Scryfall database.
    with open(newfilename, "a", encoding="utf-8") as file:
      total = len(cardstoimport)
      errors = 0
      for iteration, each in enumerate(cardstoimport):
        if iteration == 0:
          print("Preparing files, this might take a bit...")
          self.access_file()
        id = each[1]
        foil = each[2]
        quantity = each[4]
        carddata = self.getcarddatabyid(id)
        print(f"[ {iteration + 1} / {total} ] Getting data for ID: {id}")

        if carddata is None:
          print("[", iteration + 1, "/", total, "] Card could not be found from the Scryfall .json with ID:", id)
          errors = errors + 1
          continue

        number = carddata['collector_number']
        language = each[10]

        # Fix names from Scryfall to Deckbox
        name = carddata['name']
        if name == "Solitary Hunter // One of the Pack":
          name = "Solitary Hunter"

        if name in exportCards:
          exportCards[name] += quantity
        else:
          exportCards[name] = quantity
      for cardName in exportCards:
        file.write(f"{exportCards[cardName]} {cardName}\n")
    if errors > 0:
      print(f"Successfully imported {total - errors} entries into {newfilename}")
      print(f"There was {errors} error(s) finding correct IDs from the Scryfall .json. To fix this, please use a larger Scryfall bulk data file such as 'All Cards' instead of 'Default Cards'.")
    else:
      print(f"Successfully imported {total} entries into {newfilename}")

  def convertToCsv(self, dlens: str):
    #self.offlinescryfall = offlinescryfall
    # Get all cards from .dlens file
    #self.dlensc.execute('SELECT * from cards')
    cardstoimport = self.getCards(dlens)#self.dlensc.fetchall()

    # Set new .csv file name
    now = datetime.datetime.now()
    newcsvname = "output/" + now.strftime("%d_%m_%Y-%H_%M_%S") + ".csv"

    # For each card, match the id to the apk database and with scryfall_id search further data from Scryfall database.
    with open(newcsvname, "a", encoding="utf-8") as file:
      total = len(cardstoimport)
      errors = 0
      file.write(f'Count,Tradelist Count,Name,Edition,Card Number,Condition,Language,Foil,Signed,Artist Proof,Altered Art,Misprint,Promo,Textless,My Price\n')
      for iteration, each in enumerate(cardstoimport):
        if iteration == 0:
          print("Preparing files, this might take a bit...")
          self.access_file()
        id = each[1]
        foil = each[2]
        quantity = each[4]
        carddata = self.getcarddatabyid(id)
        print(f"[ {iteration + 1} / {total} ] Getting data for ID: {id}")

        if carddata is None:
          print("[", iteration + 1, "/", total, "] Card could not be found from the Scryfall .json with ID:", id)
          errors = errors + 1
          continue

        number = carddata['collector_number']
        language = each[10]

        # Fix names from Scryfall to Deckbox
        name = carddata['name']
        if name == "Solitary Hunter // One of the Pack":
          name = "Solitary Hunter"

        # Fix condition names from Scryfall to Deckbox
        condition = each[9]
        if condition == "Moderately Played":
          condition = "Played"
        elif condition == "Slighty Played":
          condition = "Good (Lightly Played)"

        # Fix set names from Scryfall to Deckbox
        set = carddata['set_name']
        if set == "Magic 2015":
          set = "Magic 2015 Core Set"
        elif set == "Magic 2014":
          set = "Magic 2014 Core Set"
        elif set == "Modern Masters 2015":
          set = "Modern Masters 2015 Edition"
        elif set == "Modern Masters 2017":
          set = "Modern Masters 2017 Edition"
        elif set == "Time Spiral Timeshifted":
          set = 'Time Spiral ""Timeshifted""'
        elif set == "Commander 2011":
          set = "Commander"
        elif set == "Friday Night Magic 2009":
          set = "Friday Night Magic"
        elif set == "DCI Promos":
          set = "WPN/Gateway"

        file.write(
          f'''"{quantity}","{quantity}","{name}","{set}","{number}","{condition}","{language}","{foil}","","","","","","",""\n''')

    if errors > 0:
      print(f"Successfully imported {total - errors} entries into {newcsvname}")
      print(f"There was {errors} error(s) finding correct IDs from the Scryfall .json. To fix this, please use a larger Scryfall bulk data file such as 'All Cards' instead of 'Default Cards'.")
    else:
      print(f"Successfully imported {total} entries into {newcsvname}")

  def connectapkdatabase(self, apkdatabase):
    apkconn = sqlite3.connect(apkdatabase)
    self.apkc = apkconn.cursor()

  def connectdlensdatabase(self, dlens):
    dlensconn = sqlite3.connect(dlens)
    self.dlensc = dlensconn.cursor()

  @lru_cache(maxsize=1)
  def access_file(self):
    try:
      with open(self.offlinescryfall, 'r', encoding='utf-8') as json_data:
        json_data = json.load(json_data)
        return json_data
    except MemoryError:
      print("Out of memory! Scryfall .json file is too large to load into memory.")
    except FileNotFoundError:
      print("Scryfall json not found.")

  @lru_cache(maxsize=128)
  def getcarddatabyid(self, id):
    t = (id,)
    self.apkc.execute('SELECT scryfall_id FROM cards WHERE _id=?', t)
    scryfall_id = self.apkc.fetchone()[0]

    try:
      for each in self.access_file():
        if each['id'] == scryfall_id:
          return each
    except TypeError:
      return None

#def main(argv):
if __name__ == "__main__":
  #main(sys.argv[1:])
  parser = argparse.ArgumentParser()
  parser.add_argument("dlens")
  parser.add_argument("-c", "--csv", action="store_true")

  dldb = "externalres/data.db"
  scryfalldb = "externalres/scryfall.json"
  app = ExportContext(scryfalldb, dldb)
  args = parser.parse_args()
  if (args.csv):
    app.convertToCsv(args.dlens)
  else:
    app.convertToDecklist(args.dlens)