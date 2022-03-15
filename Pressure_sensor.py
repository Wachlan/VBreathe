#!/usr/bin/env python3
# Program to read output from Honeywell microflow sensor with Aadvark host adaptor
# Lachlan Chow 22-3-14


#==========================================================================
# IMPORTS
#==========================================================================
from __future__ import division, with_statement, print_function
import sys
from crc import CrcCalculator, Configuration
from aardvark_py import *


#==========================================================================
# CONSTANTS
#==========================================================================
I2C_BITRATE =  100               # Set bitrate to 100 kHz (max allowed by pressure sensor)
SLAVE_ADDRESS = 0x55             # Address of pressure sensor
AADVARK_PORT = 0                 # COMPORT on PC
READ_COMMAND = b'\x36\x24'       # 3624 is the command to read triggered mass-flow calibrated differential pressure
SCALING_PRESSURE_FACTOR = 1/187  # Scaling factor for raw output to differential pressure (from datasheet)


#==========================================================================
# FUNCTIONS
#==========================================================================


def checkCRC (MSB, LSB, Expected_CRC):  # Check raw differential pressure data equals expected CRC
    data = bytes([MSB, LSB])  # Data to check
    width = 8
    poly = 0x31
    init_value = 0xFF
    final_xor_value = 0x00
    reverse_input = False
    reverse_output = False

    configuration = Configuration(width, poly, init_value, final_xor_value, reverse_input, reverse_output)

    use_table = True
    crc_calculator = CrcCalculator(configuration, use_table)

    checksum = crc_calculator.calculate_checksum(data)
    assert checksum == Expected_CRC
    assert crc_calculator.verify_checksum(data, Expected_CRC)


#==========================================================================
# MAIN PROGRAM
#==========================================================================



handle = aa_open(AADVARK_PORT)
if (handle <= 0):
    print("Unable to open Aardvark device on port %d" % AADVARK_PORT)
    print("Error code = %d" % handle)
    sys.exit()

# Ensure that the I2C subsystem is enabled
aa_configure(handle,  AA_CONFIG_SPI_I2C)

# Enable the I2C bus pullup resistors (2.2k resistors).
# This command is only effective on v2.0 hardware or greater.
# The pullup resistors on the v1.02 hardware are enabled by default.
aa_i2c_pullup(handle, AA_I2C_PULLUP_BOTH)

# Enable the Aardvark adapter's power supply.
# This command is only effective on v2.0 hardware or greater.
# The power pins on the v1.02 hardware are not enabled by default.
#aa_target_power(handle, AA_TARGET_POWER_BOTH)

# Set the bitrate
bitrate = aa_i2c_bitrate(handle, I2C_BITRATE)
print("Bitrate set to %d kHz" % bitrate)

trans_num = 0  # Counter for data written to sensor
while 1:
   

    # Write the data to the bus
    data_out = array('B', READ_COMMAND)
    count = aa_i2c_write(handle, SLAVE_ADDRESS, AA_I2C_NO_FLAGS, data_out)

    if (count < 0):  # Amount of data written less than 0 is nonsensical, give an error
        print("error: %s" % aa_status_string(count))
        break
    elif (count == 0):  # No data written, give an error
        print("error: no bytes written")
        print("  are you sure you have the right slave address?")
        break
    elif (count != len(data_out)):  # If data length does not match intended command, give an error
        print("error: only a partial number of bytes written")
        print("  (%d) instead of full (%d)" % (count, len(data_out)))
        break

    sys.stdout.write("*** Command #%02d: " % trans_num)  # Output transaction number for the user

    for i in range(count):                               # Output command for the user
        sys.stdout.write("%02x " % (data_out[i] & 0xff))
    sys.stdout.write("\n\n")

    trans_num = trans_num + 1

    # Sleep at least 135ms to make sure slave has time to process this request
    aa_sleep_ms(200)




    length = 3  # first 3 bytes of information are differential pressure MSB, differential pressure LSB and CRC (from datasheet)

    (count, data_in) = aa_i2c_read(handle, SLAVE_ADDRESS, AA_I2C_NO_FLAGS, length)  # Read the data from the sensor
    if (count < 0):  # If the amount of data read is less than 0, give an error
        print("error: %s" % aa_status_string(count))
        break
    elif (count == 0):  # If the amount of data read is less than 0, give an error
        print("error: no bytes read")
        print("  are you sure you have the right slave address?")
        break
    elif (count != length):  # If the amount of data read is not equal to the expected value, give an error
        print("error: read %d bytes (expected %d)" % (count, length))


    MSB = data_in[0]  # First byte is the MSB of pressure data
    LSB = data_in[1]  # Second byte is the LSB of pressure data
    Expected_CRC = data_in[2]  # Third byte is the CRC given by the sensor

    checkCRC(MSB, LSB, Expected_CRC)

    DP = MSB*256 + LSB
    DP = DP*SCALING_PRESSURE_FACTOR
    print ("Differential Pressure: %.1f" %DP)

    sys.stdout.write("\n")

f.close()

# Close the device
aa_close(handle)









