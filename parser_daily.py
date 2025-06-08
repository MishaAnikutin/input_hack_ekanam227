import subprocess
import json
import pandas as pd
from datetime import datetime, timedelta
import pytz
channel = 'tass_agency'
date = '2025-06-08'  #Введите дату в формате ГГГГ-ММ-ДД:

def parse_daily(channel, date):
    command = f"snscrape --since {datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d')} --jsonl telegram-channel {channel} > {channel}_today_exp.txt" 
    subprocess.run(command, shell=True)
    




#def tranformation(channel):
 #   with open(f"{channel}_today.txt") as file:
  #      file = file.readlines()
   # posts = []
    #for n,line in enumerate(file):
     #   file[n] = json.loads(file[n])
      #  posts.append(file[n])
   # print(file[0])
   # return posts
parse_daily(channel, date)

#tranformation(channel)
    






