#!/usr/bin/env python
## Application: Delete JobID from SQL server
## Written by:  Asst.Prof.Dr. Kittiphong Amnuyswat
## Updated:	    05/06/2020

import datetime
import os
import platform
from tabulate import tabulate
import pandas as pd

if platform.system() == 'Darwin' or 'Linux' :
    os.system('clear')
print("Current date and time: ", datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S"))
print("")


######################### Opening DB connection #########################
import pymysql.cursors
import sql
connection = pymysql.connect(host = sql.host,
                             user = sql.user,
                             password = sql.password,
                             db = sql.db,
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)


JobID = int(input("JobID to DELETE : "))


with connection.cursor() as cursor:
    sql = "SELECT * FROM `INCAR` WHERE `JobID` = %s"
    cursor.execute(sql,(JobID))
    result = cursor.fetchall()
connection.commit()
jobid_data = pd.DataFrame.from_dict(result)
print(tabulate(jobid_data.transpose(),tablefmt='psql'))
print()

with connection.cursor() as cursor:
    sql = "SELECT * FROM `POSCAR` WHERE `JobID` = %s"
    cursor.execute(sql,(JobID))
    result = cursor.fetchall()
connection.commit()
jobid_data = pd.DataFrame.from_dict(result)
print(tabulate(jobid_data.transpose(),tablefmt='psql'))
print()

with connection.cursor() as cursor:
    sql = "SELECT * FROM `POTCAR` WHERE `JobID` = %s"
    cursor.execute(sql,(JobID))
    result = cursor.fetchall()
connection.commit()
jobid_data = pd.DataFrame.from_dict(result)
print(tabulate(jobid_data.transpose(),tablefmt='psql'))
print()

with connection.cursor() as cursor:
    sql = "SELECT * FROM `OUTCAR` WHERE `JobID` = %s"
    cursor.execute(sql,(JobID))
    result = cursor.fetchall()
connection.commit()
jobid_data = pd.DataFrame.from_dict(result)
print(tabulate(jobid_data.transpose(),tablefmt='psql'))
print()


CF = input("Confirm delete ?? (Y) ")
if CF == 'Y' or CF == 'y' :
    with connection.cursor() as cursor:
        sql = "DELETE FROM `2020` WHERE `JobID` = %s"
        cursor.execute(sql,(JobID))
        connection.commit()

        sql = "DELETE FROM `INCAR` WHERE `JobID` = %s"
        cursor.execute(sql, (JobID))
        connection.commit()

        sql = "DELETE FROM `KPOINTS` WHERE `JobID` = %s"
        cursor.execute(sql, (JobID))
        connection.commit()

        sql = "DELETE FROM `OUTCAR` WHERE `JobID` = %s"
        cursor.execute(sql, (JobID))
        connection.commit()

        sql = "DELETE FROM `POSCAR` WHERE `JobID` = %s"
        cursor.execute(sql, (JobID))
        connection.commit()

        sql = "DELETE FROM `POTCAR` WHERE `JobID` = %s"
        cursor.execute(sql, (JobID))
        connection.commit()

        print("Delete JobID=",JobID," complete !!!")

connection.close()