#!/usr/bin/env python
## Application: Export SQL server to Google Drive CSV
## Written by:  Asst.Prof.Dr. Kittiphong Amnuyswat
## Updated:	    14/08/2020

import datetime
import os
import sys
from collections import defaultdict

import pandas as pd
import numpy as np
import pygsheets
import sql
import pymysql.cursors

sys.path.append('/Volumes/kaswat200GB/GitHub/pyVASP')
os.system('clear')
print("Export SQL server to Google Drive CSV")
print("Current date and time: ", datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S"))
print("")


connection = pymysql.connect(host=sql.host,
                             user=sql.user,
                             password=sql.password,
                             db=sql.db,
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)
with connection.cursor() as cursor:
    sql = "select * from `INCAR` \
           join `OUTCAR` on INCAR.jobid = OUTCAR.jobid \
           join `KPOINTS` on INCAR.jobid = KPOINTS.jobid \
           join `POSCAR` on INCAR.jobid = POSCAR.jobid \
           join `POTCAR` on INCAR.jobid = POTCAR.jobid "
    cursor.execute(sql)
    result = cursor.fetchall()
connection.commit()
jobid = pd.DataFrame.from_dict(result)
jobid.drop(columns=['OUTCAR.jobid','KPOINTS.jobid','POSCAR.jobid','POTCAR.jobid'])
jobid.replace(np.NaN, ' ', inplace=True)
jobid.replace('5.4.4.18Apr17-6-g9f103f2a35', '5.4.4', inplace=True)

print(jobid.head)

print("Exporting data to Google Sheet.")
client = pygsheets.authorize(service_file='/Volumes/kaswat200GB/GitHub/pyVASP/service_account.json')
sh = client.open('vasp') 
wks = sh.sheet1

wks.clear()
wks.update_value('A1', "Numbers on Stuff")
wks.set_dataframe(jobid,'A1', copy_index=False, copy_head=True,fit=True)


