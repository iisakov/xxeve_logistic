#!/usr/bin/python3
import datetime
from time import sleep
import scripts.load_info_in_table_script

scripts.load_info_in_table_script.load_stats()
load_time = ['01', '15', '30', '45']
while True:
    if datetime.datetime.now().strftime('%M') in load_time:
        print("вот теперь пора")
        scripts.load_info_in_table_script.load_stats()
    else:
        print('Ещё не время', datetime.datetime.now())
        sleep(10)



