import pywinusb.hid as hid
import time
from time import sleep
from time import gmtime, strftime
from msvcrt import kbhit
from msvcrt import getch
import random
import logging
import binascii
import threading
import sys
from sys import argv
import os
from copy import deepcopy


################################################################################
##                                                                            ##
## CLASS: UsbComms                                                            ##
##                                                                            ##
##                                                                            ##
################################################################################


class UsbComms(object):

    def __init__(self):
        self.AllDevices = []
        self.TargetDevice = []
        self.TargetDeviceReports = []
        self.ResponseReadyEvent = threading.Event()
        self.Response = []
        self.ExpectedResponses=0
        self.PacketIndex=0
        self.TempResponse = ""


    def UsbDevice_FindTargetDevice(self,mbed_vendor_id, mbed_product_id):


        usb_VIDPID = "vID=" + mbed_vendor_id.lower() + ", pID=" + mbed_product_id.lower()
        usb_vidpid = usb_VIDPID
        print(usb_vidpid)

        self.TargetDevice = 0 # Initialse this for the Close Operation

        self.AllDevices = hid.find_all_hid_devices() # Collect the HID devices from the OS
        hidList = list(self.AllDevices) #Create a list
        index=0
        TargetFound = False

        #Parse the list of HID devices for the target device

        for x in hidList:
            y = str(x)
            #print y # Display the elements of the list


            if y.find(usb_vidpid) != -1:
                targetFound= True

                self.TargetDevice=self.AllDevices[index]
                Sankyo_Card_Reader = self.TargetDevice
                TargetFound=True

            index = index +1

        if TargetFound == True:

            print(self.TargetDevice)
            return True
        else:
            return False


    def UsbDevice_Open(self):


        if not self.TargetDevice:


            return False

        else:


            self.TargetDevice.open()
            #print ('Debug Device Found');
            target_usage = hid.get_full_usage_id(0x00, 0x01)
            print(target_usage)
            self.TargetDevice.set_raw_data_handler(self.sample_handler)
            self.TargetDeviceReports = self.TargetDevice.find_output_reports()
            print(self.TargetDeviceReports)
            return True



    def UsbDevice_Close(self):


        if not self.TargetDevice:


            return False

        else:

            self.TargetDevice.close()
            return True


    def UsbDevice_Talk(self,command,packets):

        myBuffer = [0x00]*64
        tempResponse=[]
        gBuffer=bytearray.fromhex(command)   # converts hex numbers into bytearray
        myBuffer[0:0+len(gBuffer)] = gBuffer
        print(myBuffer)



        self.TargetDeviceReports[0].set_raw_data(myBuffer)
        self.ResponseReadyEvent.clear()
        self.PacketIndex=self.PacketIndex =0
        self.TempResponse = ""
        self.Response=[]
        self.TargetDeviceReports[0].send()


        self.ExpectedResponses=packets



        while self.ExpectedResponses > 0:
            if not self.ResponseReadyEvent.wait(5.0):

                    self.ExpectedResponses=0
                    self.ResponseReadyEvent.clear()
            else:
                self.ResponseReadyEvent.clear()


        self.Response= deepcopy(self.TempResponse)
        return self.Response

    def sample_handler(self,data):


        self.ExpectedResponses = self.ExpectedResponses - 1
        self.PacketIndex=self.PacketIndex +128
        i = self.PacketIndex
        binAsciiData = binascii.hexlify(memoryview(bytearray(data)))

        self.Response= deepcopy(binAsciiData)

        self.TempResponse=self.Response#self.TempResponse+deepcopy(binAsciiData)

        self.ResponseReadyEvent.set()



