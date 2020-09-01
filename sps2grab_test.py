################################################################################
#
#   Filename : Test.py
#   System   : NCR 
#
#   Module   : Main
#
#   Author   : Alexander W. Whytock
#
#
################################################################################
#
#        COPYRIGHT (c) NCR CORPORATION
#        2015 DAYTON,OHIO,USA
#        DESIGN CONTROL ORGANISATION:-
#        NEW PRODUCT DEVICES, DUNDEE
#        FSG
#
################################################################################
#
#        MODIFICATION OF SOURCE CODE BY OTHER THAN THE DESIGN
#        CONTROL ORGANISATION IS PROHIBITED.
#
#        THIS PROGRAM AND ALL INFORMATION CONTAINED HEREIN IS THE
#        PROPERTY OF NCR CORPORATION AND ALL UNAUTHORISED USE AND
#        REPRODUCTION IS PROHIBITED.
#
################################################################################
#
#   Version  History:
#
#
################################################################################


################################################################################
##                                                                            ##
## PYTHON & XML TEST ENVIRONMENT FOR NCR USB DEVICES                          ##
##                                                                            ##
##                                                                            ##
################################################################################
##                                                                            ##
##                                                                            ##
################################################################################


################################################################################
##                                                                            ##
## IMPORTS                                                                    ##
##                                                                            ##
################################################################################




import time
from time import sleep
from time import gmtime, strftime
from msvcrt import kbhit
from msvcrt import getch
import random
import logging

import unittest
import xml.etree.ElementTree as ET
import binascii
import threading
from array import array

from binascii import unhexlify
from sys import argv
import csv
import sys
import datetime
import math

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import Csv_HandlerV4p3
from GenericUsbClass import UsbComms as myUsbComms





all_devices=[0x00]*8
deviceOne = myUsbComms()

################################################################################
##                                                                            ##
## CLASS Mem: Container for globals. A bit of a cheat but less bad            ##
##                                                                            ##
################################################################################

class Mem():
    gBuffer = [0x00]*63
    gExpected = [0x00]*63
    gWait = 0
    gDelay = 0
    gFailed = 0
    gResponseReceived = 0
    gResponseReadyEvent = threading.Event()
    gExpectedResponses=0
    gFailureCount=0
    gUnmatchedResponses=0
    gChekResponse="TRUE"
    gAdcValue=0
    sw2ButtonValue = 0
    sw3ButtonValue = 0
    led_frequency = ""
    led_pattern = ""

    gTempValue=35
    gDisruptorStatus=0
    gDistanceValue=6000
    gGradientValue=6000
    
    gAdcValue_Min=0
    gTempValue_Min=64000
    gDistanceValue_Min=64000
    gGradientValue_Min=64000
    
    gAdcValue_Max=100
    gTempValue_Max=0
    gDistanceValue_Max=0
    gGradientValue_Max=0
    gMyCsvFile="test.csv"
    
    gRunningAverageBuffer = [0x00]*11
    gBaseLineCalculation = 30
    gBaseline = 0 
    gTEMPC=0
    gCAP1=0
    gCAP2=0
    gCAP3=0
    gCAP4=0
    gCAP5=0
    gCAP6=0
    gCAP7=0
    gCAP8=0
    gCAP9=0
    gCAP10=0
    gCAP11=0
    gCAP12=0
    gCapAdcValue_Var=0
    gCapAdcValue_Avg=0
    gCapAdcValue_Diff=0
    gCapAdcValue_Last=0
    
    g_x_min=64000
    g_x_max=-64000
    gFirstMeasurement=0
    gCalibration=0
    gCap1_norm=0
    
    gRawAdcValue=0
    gPatternStrDefault = ["0101","0202","0303","0404","0505","0606","0707","0808","0909","0A0A","0B0B","0C0C"]
    gPatternSensorListDefault = [1,2,3,4,5,6,7,8,9,10,11,12]
    gPatternStr = []
    gPatternSensorList =[]
    gPatternStrLength = 2
    gPatternSensor=4
    #gPatternStr = ["0A0A","0707","0707","0707","0707","0707","0707","0707"]
    gPatternIndex=0
    gPatternStartTime= time.time()
    gPatternElapsedTime= gPatternStartTime
 
################################################################################
##                                                                            ##
## FUNCTION: Max                                                              ##
##                                                                            ## 
## Compare two integers. Return the greater value.                            ##
##                                                                            ##
################################################################################	
def Max(x,max):

    ReturnValue=max
    
   
    if (x > max):
        ReturnValue=x
    
    return(ReturnValue)
    
################################################################################
##                                                                            ##
## FUNCTION: Min                                                              ##
##                                                                            ## 
## Compare two integers. Return the lesser value.                             ##
##                                                                            ##
################################################################################
def Min(x,min):
        
    ReturnValue=min
          
    if (x < min): 
        ReturnValue=x
    return(ReturnValue)






################################################################################
##                                                                            ##
## Set up the graphs                                                          ## 
##                                                                            ##
################################################################################


#app = QtGui.QApplication([])

mem = Mem()
print("Serial Port")
if len(argv) > 2:
    comPort = 'COM3'
else:
    if len(argv) == 2:
        comPort = str(argv[1])
    else:
        comPort = 'COM3'   
	


pg.setConfigOptions(antialias=True)
pg.setConfigOption('background', 'w')
win = pg.GraphicsWindow(title="SPS2")
win.resize(1000,1000)
win.setWindowTitle('SPS2 Tutorial Plots')

print("Window Ready")

led1 = win.addLabel("")

win.nextRow()
win.nextRow()

p1 = win.addPlot()
data1a = [0x00]*100
curve1a = p1.plot(data1a)
p1.setTitle(title="ADC Percentage")
p1.showGrid(x=True, y=True, alpha=0.75)
ptr1 = 0
win.nextRow()


p2 = win.addPlot()
data2a = [0x00]*100
curve2c = p2.plot(data2a)
p2.setTitle(title="SW2 Button " + str(mem.sw2ButtonValue))
p2.showGrid(x=True, y=True, alpha=0.75)


ptr2 = 0
win.nextRow()


p3 = win.addPlot()
data3a = [0x00]*100
curve3c = p3.plot(data3a)
p3.setTitle(title="SW3 Button")
p3.showGrid(x=True, y=True, alpha=0.75)
ptr3 = 0


win.nextRow()



print("Plots Ready")



################################################################################
##                                                                            ##
## FUNCTION: Calibration                                                      ##
##                                                                            ## 
## For 100 samples this procedure will record key signal characteristics.     ##
##                                                                            ##
################################################################################
def  Calibration():

    #print("Calibration Check")  
    if (mem.gFirstMeasurement==1):
        
        #print("Max",mem.g_x_max)
        #print("Min",mem.g_x_min)
        Mint=0
    else:
        print("Learning")    
        if (mem.gCalibration < 100):
            mem.gCalibration=mem.gCalibration+1
            
        else:
            mem.gFirstMeasurement=1
            
        
        mem.g_x_max=Max(mem.gCAP1,mem.g_x_max)
        mem.g_x_min=Min(mem.gCAP1,mem.g_x_min)
        
        
        #print("Max",mem.g_x_max)
        #print("Min",mem.g_x_min)
   


#End Calibration()


################################################################################
##                                                                            ##
## FUNCTION: update                                                           ##
##                                                                            ## 
## Update the graphs.                                                         ##
##                                                                            ##
################################################################################

def update():
    global ptr1,data1a,curve1a
    global ptr2,data2a,curve2c, p1
    global ptr3,data3a,curve3c
    
    # runningAverage() 
    
    data1a[:-1] = data1a[1:]
    data1a[-1] = mem.gAdcValue
    curve1a.setData(data1a,pen='r')
    
    ptr1 += 1
    
    

    
    data2a[:-1] = data2a[1:]
    data2a[-1] = mem.sw2ButtonValue
    curve2c.setData(data2a,pen='m')
    
    ptr2 += 1


    data3a[:-1] = data3a[1:]
    data3a[-1] = mem.sw3ButtonValue
    curve3c.setData(data3a,pen='m')
    
    ptr3 += 1
    if mem.led_pattern != "" and mem.led_pattern != "":
        text = pg.TextItem(text="Last Led Pattern = " + str(mem.led_pattern) + "\nLed Frequency = " + str(int(mem.led_frequency)) + " (ms)", color=(169, 169, 169), html=None, anchor=(0, 0), border=None, fill=None, angle=0, rotateAxis=None)
        text.setParentItem(led1)
        font=QtGui.QFont()
        font.setPixelSize(16)
        text.setFont(font)
    
    win.nextRow()
  
    
    UsbStuff()
    myAdc= [0x00]*2
    Calibration()
    
    


timer = QtCore.QTimer()
timer.timeout.connect(update)
print("Timers Ready")   
timer.start(0.1)#was 400
print("Timers Started") 

################################################################################
##                                                                            ##
## FUNCTION: Ascii Conversion                                                 ##
##                                                                            ## 
## Convert hex into ascii character.                                          ##
##                                                                            ##
################################################################################

def asciiConversion(hex_string):
    bytes_object = bytes.fromhex(hex_string)
    ascii_string = bytes_object.decode("ASCII")
    return ascii_string
    
def UsbStuff():

    which_sensor = mem.gPatternIndex
    testSuiteStart = time.time()
    mem.gResponseReadyEvent.clear()
    mem.gFailureCount=0
    myBuffer = [0x00]*63
    myCrc = [0x00]*2
    myReport = [0x01]*1
    buf=[0x00]*4
    
    mem.gFailed = 0
    mem.gMultipleResponses = 0 
    mem.gExpectedResponses=0
    description = "SPS Raw Data"
    prompt_text="No Prompt"#test.find('prompt_text').text
    mem.gWait =    0#wait

    mem.gDelay = 0#delay 	
    
    mem.gPatternElapsedTime = time.time()
    print("+==============================================================+")
    print("Pattern = ",f'{mem.gPatternStr[mem.gPatternIndex]:10}          |')
    print("+--------------------------------------------------------------+")
    #Github Test 2
    if (mem.gPatternElapsedTime - mem.gPatternStartTime > 10):
        mem.gPatternIndex=mem.gPatternIndex+1
        if (mem.gPatternIndex > mem.gPatternStrLength-1):
            mem.gPatternIndex=0
        

        CommandStr = "010300633830"
        print("+--------------------------------------------------------------+")
        print("| Change Over                                                  |")    
        print("+==============================================================+")
        print("| Wait for 1 Second                                            |") 
        print("+--------------------------------------------------------------+")
        response = ""
        response = deviceOne.UsbDevice_Talk(CommandStr,1)
        #print(response)		
        time.sleep(1)    
        mem.gPatternStartTime = time.time()
        response = deviceOne.UsbDevice_Talk(CommandStr,1)
        response = deviceOne.UsbDevice_Talk(CommandStr,1)
        response = deviceOne.UsbDevice_Talk(CommandStr,1)
        mem.gPatternStartTime = time.time()


    CommandStr = "010300633830"
    response = ""
    response = deviceOne.UsbDevice_Talk(CommandStr,1)

    encoding = 'utf-8'
    encodedResponse=str(response, encoding)
    
    led = encodedResponse[70:80]
    
    buf[3] = encodedResponse[58:60]
    buf[2] = encodedResponse[66:68]
    buf[1] = encodedResponse[64:66]
    buf[0] = int(response[60:62],16)

    if buf[1] == "6e":
        mem.sw2ButtonValue = 0
    else:
        mem.sw2ButtonValue = 1

    if buf[2] == "6e":
        mem.sw3ButtonValue = 0
    else:
        mem.sw3ButtonValue = 1

    if str(led) == "ffffffffff":
        mem.led_frequency = 0
    else:
        mem.led_frequency = bytearray.fromhex(led).decode()

    
    mem.led_pattern = asciiConversion(buf[3])

    print(mem.led_pattern)

    print(str(led))
    print("+--------------------------------------------------------------+")
    print("ADC Value = ",f'{buf[0]}                                       |')
    print("+--------------------------------------------------------------+")
    print("+==============================================================+")

    mem.gPatternSensor=mem.gPatternSensorList[mem.gPatternIndex]
    mem.gRawAdcValue=buf[0]    
    
    mem.gAdcValue=mem.gRawAdcValue   
        
    mem.gCAP2=mem.sw2ButtonValue
    mem.gCAP3=mem.sw3ButtonValue
    mem.gCAP4=mem.gAdcValue
    
    response=""
    mem.gExpected=bytearray.fromhex(response)

    myBuffer=""

    myBuffer = myBuffer+str(mem.gCAP2) + ","
    myBuffer = myBuffer+str(mem.gCAP3) + ","
    myBuffer = myBuffer+str(mem.gCAP4) + ","
    myBuffer = myBuffer+str(mem.led_pattern) + ","
    myBuffer = myBuffer+str(mem.led_frequency) + ","
    
    
    csv_handler.Update(myBuffer)

    print(myBuffer)

    
    if mem.gFailed == 1:
        a=1
    else:
        a=0
    
    testSuiteEnd = time.time()
    testSuiteElapsedTime = testSuiteEnd-testSuiteStart

#END UsbStuff
############################################    
################################################################################
##                                                                            ##
## FUNCTION: findMyDevice                                                     ##
##                                                                            ## 
## Locates the device on usb using the vid & pid. Uses imported module        ##
## pywinusb.sp                                                                ##
##                                                                            ##
################################################################################	
	
def findMyDevice(myDevice,mbed_vendor_id, mbed_product_id):
    all_devices = hid.HidDeviceFilter(vendor_id = mbed_vendor_id, product_id = mbed_product_id).get_devices()
    myDevice=all_devices[0]		           
 
################################################################################
##                                                                            ##
## FUNCTION: sample_handler.                                                  ##
##                                                                            ## 
## Call back to receive response from the device. Uses a mem.global event to  ##
## signal response arrival. Also compares the response with the expected      ##
## response and signals pass or fail.                                         ##
##                                                                            ##
################################################################################	

def sample_handler(data):
    myAdc	= [0x00]*2
    myTemp= [0x00]*2
    myGradient = [0x00]*2
    myDistance = [0x00]*2
    myFpga = [0x00]*2
    mem.gExpectedResponses = mem.gExpectedResponses - 1    
    ##print("Raw data: {0}".format(data))
    ##print binascii.hexlify(memoryview(bytearray(data)))
    binAsciiData = binascii.hexlify(memoryview(bytearray(data)))
    binAsciiExpected = binascii.hexlify(memoryview(bytearray(mem.gExpected)))
    logging.info('  |-   Actual Response  : %s',binAsciiData)

    #if not binAsciiData ==binAsciiExpected:
    x=binascii.unhexlify(binAsciiData)
    #x=x.upper()
    y=binascii.unhexlify(binAsciiExpected)	
    #y=y.upper()
    ##print x
    ##print y
    
    if mem.gCheckResponse=="TRUE":
        ##print x.find(y)
        if x.find(y) ==  -1:
           logging.info('  |-   %s','*** Response Not Matched ***')	
           logging.info('  |-   Expected Response: %s',binAsciiExpected)
           logging.info('  |-   Actual           : %s',binAsciiData)
           ##print('Response Not Matched')
           #print ' |->  *** Result ==== Response Not Matched ***' 
           #print ' |->  ' 
           mem.gFailed=1
           mem.gUnmatchedResponses= mem.gUnmatchedResponses+1	   
           mem.gFailureCount = mem.gFailureCount+1

           l=Dif(binAsciiExpected, binAsciiData)
           for i in range(len(l)):
            #print ' |->  Mismatch at position ', l[i], 'Expected ', binAsciiExpected[l[i]], ' Actual ',binAsciiData[l[i]]
            logging.info('  |->  Mismatch at position %s Expected %s Actual %s',l[i],binAsciiExpected[l[i]],binAsciiData[l[i]])
        else:
            #print ' |->   Result ==== OK' 
            #print ' |->  ' 
            logging.info('  |-   %s','Result ==== Response Matched')
            logging.info('  |-   Expected Response: %s',binAsciiExpected)

    else:
        ##print ' |-> Unchecked Response'
        logging.info('  |- Uncheck Response')
        logging.info('  |- Raw Data   : %s',binAsciiData)
        length=0
        
        if (data[4]==0x32):
            
            if (data[5]==0x31):
                index=10
                length=1
                rawLength=2
                outBuffer = data[11:11+rawLength]
                myAdc[0] = outBuffer[1]
                myAdc[1] = outBuffer[0]
                #print '  |-> Length : ',length
                #print '  |-> ADC Value: ',binascii.hexlify(memoryview(bytearray(myAdc)))
                logging.info('  |-   ADC Value: %s',binascii.b2a_qp(memoryview(bytearray(outBuffer))))
                
                #Temperature
                myTemperatureBuffer = data[17:19]
                myTemp[0] = myTemperatureBuffer[1]
                myTemp[1] = myTemperatureBuffer[0]
                
                myGradientBuffer = data[15:17]
                myGradient[0] = myGradientBuffer[1]
                myGradient[1] = myGradientBuffer[0]
                #print '  |-> Gradient Value: ',binascii.hexlify(memoryview(bytearray(myGradient)))
                strGradient=binascii.hexlify(memoryview(bytearray(myGradient)))
                mem.gGradientValue=int(strGradient,16)
                
                
                myDistanceBuffer = data[13:15]
                myDistance[0] = myDistanceBuffer[1]
                myDistance[1] = myDistanceBuffer[0]
                #print '  |-> Distance Value: ',binascii.hexlify(memoryview(bytearray(myDistance)))
                strDistance=binascii.hexlify(memoryview(bytearray(myDistance)))
                mem.gDistanceValue=int(strDistance,16)
                
                logging.info('  |-   Temperature Value: %s',binascii.b2a_qp(memoryview(bytearray(myTemperatureBuffer))))
                strTemp = binascii.hexlify(memoryview(bytearray(myTemp)))
                #strAdc="7FFF"
                #x= -1
                ##print 'x1',x	
                
                tx= int(strTemp,16)
                #print 'tx hex',tx
                if ((tx & 0x80)==0x80):
                     ty = tx ^ 0x80
                     ty=-ty
                    
                else:
                    ty=tx
                #print 'Temperature ty', ty
                    
                mem.gTempValue=ty
                CsvHandler(myAdc)
            else:
            	if (data[5]==0x32):
                    index=8
                    length = data[index]
                    rawLength=length*2
                    outBuffer = data[9:9+rawLength]
                    adc_index=rawLength
                    #print 'Initial:', adc_index
                    #print 'ADC Length:',  rawLength
                    for adc_index in range(0,rawLength,2):
                        #print 'Pre:',adc_index
                        myAdc[0] = outBuffer[adc_index+1]
                        myAdc[1] = outBuffer[adc_index]
                        #print '  |-> Length : ',length
                        #print '  |-> ADC Value: ',binascii.hexlify(memoryview(bytearray(myAdc)))
                        logging.info('  |-   ADC Value: %s',binascii.hexlify(memoryview(bytearray(myAdc))))
                        CsvHandler(myAdc)
        else:
            if ((data[4]==0x31) and (data[5]==0x33)):
                if (data[35]==0x41):
                    #print 'DISRUPTOR: OFF'
                    mem.gDisruptorStatus=0
                    if (data[36]==0x35):
                        #print 'DISRUPTOR: ON FPGA'
                        mem.gDisruptorStatus=2
                else:
                    if (data[35]==0x40):
                        #print 'DISRUPTOR: ON'
                        mem.gDisruptorStatus=1
                    else:
                        #print 'DISRUPTOR: ERROR'
                        mem.gDisruptorStatus=-1
                        
                
    
    mem.gResponseReadyEvent.set()  
    ##print mem.gResponseReadyEvent.isSet()
    ##print ' |-  ', binAsciiData
    #print ' |->  ' 
    #print ' |->  '                
                
                
################################################################################
##                                                                            ##
## FUNCTION: main                                                             ##
##                                                                            ## 
## Initialisation & parses the xml file file.xml. Calls talkMyDevice.         ##
## Logs to test.log                                                           ##
##                                                                            ##
################################################################################




if __name__ == '__main__':
   
    myList = []
    pattern = [4,5,6,7,8,9,10,11,12]    
    patten_length=9
        
    if len(argv) > 1:
        if len(argv) < 14:
            for i in range(1,len(argv)):
                myList.append(int(argv[i]))  
            
            res = [] 
            for i in myList: 
                if i not in res: 
                    res.append(i)    
            pattern = sorted(res)
   
    
    for i in range(len(pattern)):
        print(pattern[i])  
    
    gPatternStrDefault = ["0101","0202","0303","0404","0505","0606","0707","0808","0909","0A0A","0B0B","0C0C"]
    gPatternSensorListDefault = [1,2,3,4,5,6,7,8,9,10,11,12]
    
    for i in range(len(pattern)):
        index=pattern[i]-1
        mem.gPatternStr.append(gPatternStrDefault[index])
        mem.gPatternSensorList.append(gPatternSensorListDefault[index])
        
    
    mem.gPatternStrLength=len(mem.gPatternStr)
    print("Length = ",mem.gPatternStrLength)
    
   

    for i in range(len(mem.gPatternStr)):
        print("Pattern =",mem.gPatternSensorList[i]," ",mem.gPatternStr[i])     
        

    #exit() 

    if (deviceOne.UsbDevice_FindTargetDevice("0x04D8", "0x003F") == True):

        if (deviceOne.UsbDevice_Open() == True):
            
            print ('|-> USBSPS2 ATTACHED')

            

    myfile = argv[0].replace(".py",".log",1)
    mem.gMyCsvFile = argv[0].replace(".py",".csv",1)
    print(mem.gMyCsvFile)
    csv_handler = Csv_HandlerV4p3.csvHandler(Mem.gMyCsvFile)
    print("Csv Ready")
	
    ##logging.basicConfig(format='%(asctime)s.%(msecs)3d %(message)s', datefmt='%Y/%m/%d %H:%M:%S',level=#logging.NOTSET,filemode='w',filename=myfile)
    CommandStr = ""
    CommandStr = "010500633337"+mem.gPatternStr[mem.gPatternIndex]
    print(CommandStr)
    response = ""
    response = deviceOne.UsbDevice_Talk("010300633830",1)
    
    
## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
        print("Main Loop Started")

