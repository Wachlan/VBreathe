#!/usr/bin/env python3.8
# Program to read output from Honeywell microflow sensor with Aadvark host adaptor
# Lachlan Chow 22-3-14


#==========================================================================
# IMPORTS
#==========================================================================
from __future__ import division, with_statement, print_function
import sys
import time
import datetime
import csv
import statistics
from aardvark_py import *


#==========================================================================
# CONSTANTS
#==========================================================================
I2C_BITRATE =  400               # Set bitrate to 100 kHz (max allowed by pressure sensor)
SLAVE_ADDRESS = 0x28             # Address of microforce sensor
AADVARK_PORT = 0                 # COMPORT on PC
OUTPUT_MIN = 3277                # Minimum output of sensor (20% of 2^14)
OUTPUT_MAX = 13107               # Maximum output of sensor (80% of 2^14)


#==========================================================================
# MAIN PROGRAM
#==========================================================================


handle = aa_open(AADVARK_PORT)
if (handle <= 0):
    print("Unable to open Aardvark device on port %d" % AADVARK_PORT)
    print("Error code = %d" % handle)
    sys.exit()

# Ensure that the I2C subsystem is enabled with GPIO to provide 3.3V power source
# The I2C power is 5V which is too much for the sensor
aa_configure(handle,  AA_CONFIG_GPIO_I2C)

# Enable the I2C bus pullup resistors (2.2k resistors).
# This command is only effective on v2.0 hardware or greater.
# The pullup resistors on the v1.02 hardware are enabled by default.
aa_i2c_pullup(handle, AA_I2C_PULLUP_BOTH)

# Enable the Aardvark adapter's power supply.
# This command is only effective on v2.0 hardware or greater.
# The power pins on the v1.02 hardware are not enabled by default.
#aa_target_power(handle, AA_TARGET_POWER_BOTH)

# Set GPIO 03 (pin 7) to output with magnitude 1 to power the sensor
aa_gpio_set (handle, AA_GPIO_SCK);

# Set the bitrate
bitrate = aa_i2c_bitrate(handle, I2C_BITRATE)
#print("Bitrate set to %d kHz" % bitrate)



data = []
data_raw = []
timestr = time.strftime("%Y%m%d-%H%M%S")
filename = 'Microforce_readings_'+ timestr + '.csv'
fields = ['Time', 'Gel weight (g)', 'Average Force (N)', 'Standard Deviation (N)', 'Average Force (counts)','Standard Deviation (counts)']

with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(fields)


while 1:
    writeFlag = 1
    print("For the first 20 seconds, the values will be displayed but not recorded. For the last 10 seconds, values will be recorded.")
    gelWeight = input("Enter the gel cup weight in grams: ")
    timeout_start = time.time()
    data = []
    data_raw = []

    # Take measurements for 30 seconds. For the first 20 seconds, the values will be displayed but not recorded. For the last 10 seconds, values will be recorded.
    while time.time() <= timeout_start + 30:

        # Take data point every 0.2 seconds
        aa_sleep_ms(200)


        length = 4  # first 2 bytes of information are microforce MSB and microforce LSB, temperature reading not taken

        (count, data_in) = aa_i2c_read(handle, SLAVE_ADDRESS, AA_I2C_NO_FLAGS, length)  # Read the data from the sensor
        if (count < 0):  # If the amount of data read is less than 0, give an error
            print("error: %s" % aa_status_string(count))
            break
        elif (count == 0):  # If the amount of data read is less than 0, give an error
            print("error: no bytes read")
            print("Are you sure you have the right slave address?")
        elif (count != length):  # If the amount of data read is not equal to the expected value, give an error
            print("error: read %d bytes (expected %d)" % (count, length))


        Force_raw = ((data_in[0] << 8) | data_in[1]) # first 2 bytes of information are microforce MSB and microforce LSB
        Force_Newtons = ((Force_raw - OUTPUT_MIN)/(OUTPUT_MAX - OUTPUT_MIN))*(15) # formula from user manual


        if time.time() >= timeout_start + 20 and time.time() <= timeout_start + 20.2:
            data = []
            data_raw = []
            print ("-------------------------- Data recording started -------------------------- ")

        # Data processing for Newtons
        data.append(Force_Newtons)
        runningAverage = sum(data)/len(data)
        standardDeviation = statistics.pstdev(data)

        # Procesing for raw data
        data_raw.append(Force_raw)
        runningAverage_raw = sum(data_raw)/len(data_raw)
        standardDeviation_raw = statistics.pstdev(data_raw)

        # Print out values for user
        print ("Force: %.2f N   Raw value: %.2f counts" %(Force_Newtons, Force_raw))
        print ("Running average and standard deviation: %.2f N %.2f N    Raw values: %.2f counts %.2f counts \n" %(runningAverage, standardDeviation, runningAverage_raw, standardDeviation_raw))


        if time.time() >= timeout_start + 29.8 and writeFlag == 1:
            writeFlag = 0
            # Write data to CSV file
            timestamp_now = datetime.datetime.now()
            row_contents = [timestamp_now, gelWeight, runningAverage, standardDeviation, runningAverage_raw, standardDeviation_raw]

            # open the file in the write mode
            with open(filename, 'a+', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(row_contents)
                print("Data recorded in CSV file \n")

            break




# Close the device
aa_close(handle)
























