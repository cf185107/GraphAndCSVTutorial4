import time
from time import sleep
from time import gmtime, strftime
from msvcrt import kbhit
from msvcrt import getch
import random
import binascii
import threading
from array import array
from binascii import unhexlify
from sys import argv
import csv
import sys
import datetime
import math
import os
import platform


class csvHandler:              

    def __init__( self,fname):
        
        self.name = fname
        self.shortname=fname
        self.queue = []
        currentTime=datetime.datetime.now()
        strDate =currentTime.strftime("%Y%m%d")
        strTime = currentTime.strftime("%H%M%S")
        
        
        
        try:
                        myCsvFile = strDate + strTime + self.name
                        self.name=myCsvFile
                        with open(myCsvFile, 'a', encoding='utf-8',newline='\n') as csvfile: #ab+
                                        fieldnames = ['date', 'time','utc','SW2 Button', 'SW3 Button','ADC (%)', 'LED Pattern', 'LED Frequency']
                                        writer = csv.DictWriter(csvfile, delimiter=',',  fieldnames=fieldnames,lineterminator='\n')
                                        writer.writeheader()
                                        print("Post Write Header")
        except csv.Error as e:
                        sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))

    def Update(self,buffer):
                
        i=0
        
        fields = []
        for i in range(6):
            fields.append(i)
        
        self.stuff= buffer
        currentTime=datetime.datetime.now()
        strDate =currentTime.strftime("%Y/%m/%d")
        strTime = currentTime.strftime("%H:%M:%S.%f")
        utc = int(round(time.time() * 1000))
        print(utc)
        
        numberOfItems = self.stuff.count(",")+1
        #print(numberOfItems)
        i=0
        while i < numberOfItems-1:
            fields[i] = float(buffer.split(",")[i])
            i=i+1
        
        try:
            with open(self.name, 'a',newline='\n') as csvfile:
                    fieldnames = ['date', 'time','utc','SW2 Button', 'SW3 Button','ADC (%)', 'LED Pattern', 'LED Frequency'] 
                    writer = csv.DictWriter(csvfile, delimiter=',',  fieldnames=fieldnames,lineterminator='\n')
                    
                    writer.writerow({'date': strDate, 'time': strTime,'utc':utc, 'SW2 Button': fields[0], 'SW3 Button': fields[1],'ADC (%)': fields[2],'LED Pattern': fields[3],'LED Frequency': fields[4]})
                   
                    
        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))
                        
        fSize= os.path.getsize(self.name)
        if ((fSize) +1024 >0x200000):#0x200000):
                           
            try:
                currentTime=datetime.datetime.now()
                strDate =currentTime.strftime("%Y%m%d")
                strTime = currentTime.strftime("%H%M%S")
                myCsvFile = strDate + strTime + self.shortname
                self.name=myCsvFile
                with open(myCsvFile, 'a',newline='\n') as csvfile:
                    fieldnames = ['date', 'time','utc','SW2 Button', 'SW3 Button','ADC (%)', 'LED Pattern', 'LED Frequency'] 
                    writer = csv.DictWriter(csvfile, delimiter=',',  fieldnames=fieldnames,lineterminator='\n')
                    writer.writeheader()
            except csv.Error as e:
                sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))
                        
        
                                
