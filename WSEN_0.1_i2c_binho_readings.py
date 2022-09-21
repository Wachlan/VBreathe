#!/usr/bin/env python3



import sys
import time
import datetime
import csv
import numpy as np

# import the binho library
from binho import binhoHostAdapter

# These imports help us handle errors gracefully
import errno
from serial import SerialException
from binho.errors import DeviceNotFoundError, BinhoException

# Included for demonstrating the various ways to find and connect to Binho host adapters
# be sure to change them to match you device ID / comport
targetComport = "COM5"
targetDeviceID = "0X8735CDA350533251382E3120FF0A0839"

# Start by finding the desired host adapter and connecting to it
# wrap this with try/except to elegantly capture any connection errors
try:

    # grab the first device found the system finds
    binho = binhoHostAdapter()

    # When working with multiple host adapters connected to the same system
    # you can use any of the following methods to connect:

    # 1) grab the device with a specific index
    # binho = binhoHostAdapter(index=0)

    # 2) or get the device using the COM port
    # binho = binhoHostAdapter(port=targetComport)

    # 3) or get the device using the deviceID number
    # binho = binhoHostAdapter(deviceID = targetDeviceID)

except SerialException:

    print(
        "The target Binho host adapter was found, but failed to connect because another application already has an open\
         connection to it.",
        file=sys.stderr,
    )
    print(
        "Please close the connection in the other application and try again.",
        file=sys.stderr,
    )
    sys.exit(errno.ENODEV)

except DeviceNotFoundError:

    print(
        "No Binho host adapter found on serial port '{}'.".format(targetComport),
        file=sys.stderr,
    )
    sys.exit(errno.ENODEV)


# Once we made it this for, the connection to the device is open.
# wrap this with try/except to elegantly capture any errors and manage closing the
# connection to the host adapter automatically
try:

    if binho.inBootloaderMode:
        print(
            "{} found on {}, but it cannot be used now because it's in DFU mode".format(
                binho.productName, binho.commPort
            )
        )
        sys.exit(errno.ENODEV)

    elif binho.inDAPLinkMode:
        print(
            "{} found on {}, but it cannot be used now because it's in DAPlink mode".format(
                binho.productName, binho.commPort
            )
        )
        print("Tip: Exit DAPLink mode using 'binho daplink -q' command")
        sys.exit(errno.ENODEV)

    else:
        print("Connected to a {} (deviceID: {}) on {}".format(binho.productName, binho.deviceID, binho.commPort))

    # set the host adapter operationMode to 'I2C'
    binho.operationMode = "I2C"

    binho.i2c.frequency = 100000
    binho.i2c.useInternalPullUps = True

    # Let's start by looking at the default I2C bus settings
    print("I2C bus configuration:")
    print("Clk Freq: {} Hz, Use Internal PullUps: {}".format(binho.i2c.frequency, binho.i2c.useInternalPullUps))
    print()

    # The clock frequency can be configured to our desired frequency as shown below
    # binho.i2c.frequency = 100000
    # binho.i2c.frequency = 400000
    # binho.i2c.frequency = 1000000
    # binho.i2c.frequency = 3400000

    # The internal pullup resistors can be controlled as shown below
    # binho.i2c.useInternalPullUps = False
    

    # Let's scan for a list of I2C peripheral devices on the bus and display the results.
    # You'll want to have at least 1 I2C device connected for this example
    scanResults = binho.i2c.scan()

    #print("Found {} I2C devices on the bus:".format(len(scanResults)))
    #print(scanResults)
    #print()

    # Hint: If you want to print the device list to the console in a much more human-friendly format
    # you can do it this way:
    print("Found {} I2C devices on the bus:".format(len(scanResults)))
    print("[{}]".format(", ".join(hex(x) for x in scanResults)))
    print()

    # We need to have at least one device on the bus for the rest of the
    # example to be meaningful
    if len(scanResults) > 0:

        # lets target the first device that was found
        targetDeviceAddress = scanResults[0]

    else:

        raise RuntimeError("No I2C Devices found, please connect a device to run the rest of the example.")

    # We know there's a device on the bus if we made it this far
    # so let's try to do a simple read from the device

    # Read 2 bytes from the target i2c device. This function returns the read
    # data, and will raise an exception if the read did not succeed.

    # rxData = []

    #try:
    #    rxData = binho.i2c.read(targetDeviceAddress, 2)
    #    print(rxData)

    #except BinhoException:
    #    print("I2C Read Transaction failed!")

    #print()

    # The data is a byte array, which is easy to work with programmatically, but if you'd like to
    # print it to the console in a more human-friendly format, try this
    #rcvdBytes = "Read {} byte(s):\t".format(len(rxData))
    #for byte in rxData:
    #    rcvdBytes += "\t " + "0x{:02x}".format(byte)

    #print(rcvdBytes)
    #print()

    # Start measurement
    # No write comand is necessary



    # We know there's a device on the bus if we made it this far
    # so let's try to do a simple read from the device

    # Read 2 bytes from the target i2c device. This function returns the read
    # data, and will raise an exception if the read did not succeed.

    rxData = []
    bytesToRead = 4

    try:
        rxData = binho.i2c.read(targetDeviceAddress, bytesToRead)
        #print(rxData)

    except BinhoException:
        print("I2C Read Transaction failed!")

    print()

    # The data is a byte array, which is easy to work with programmatically, but if you'd like to
    # print it to the console in a more human-friendly format, try this
    # rcvdBytes = "Read {} byte(s):\t".format(len(rxData))
    # for byte in rxData:
    #    rcvdBytes += "\t " + "0x{:02x}".format(byte)

    # print(rcvdBytes)
    # print()

    # Of course, it's very common to write and read to the device within the same transaction - as in when performing
    # a read register action. To make this easy, we'll use the transfer
    # function
    # writeData = [0x03, 0xC4]
    # bytesToRead = 24

    # Just like the i2c.read function, this will return data and raise an
    # exception if the transaction fails.
    # rxData = []

    # try:
    #     rxData = binho.i2c.transfer(targetDeviceAddress, writeData, bytesToRead)

    # except BinhoException:
    #     print("I2C Transfer Transaction failed!")

    # else:
    #     print("I2C Transfer Succeeded: ")
    #     sentBytes = "Wrote {} byte(s):".format(len(writeData))

    #     for byte in writeData:
    #         sentBytes += "\t " + "0x{:02x}".format(byte)

    #     rcvdBytes = "Read {} byte(s):\t".format(len(rxData))
    #     for byte in rxData:
    #         rcvdBytes += "\t " + "0x{:02x}".format(byte)

    #     print(sentBytes)
    #     print(rcvdBytes)

    # print()

    timeout = 0.5 # seconds

    timeout_start = time.time()

    timestr = time.strftime("%Y%m%d-%H%M%S")
    # print (timestr)
    filename = 'WSEN_readings_'+ timestr + '.csv'
    # print (filename)

    fields = ['timestamp', 'pressure raw', 'pressure (Pa)', 'temperature']

    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(fields)

    data = []

    try:
        while 1:
            #while time.time() >= timeout_start + timeout:
            while time.time() <= timeout_start + 15:

                # Start measurement
                rxData = []
                bytesToRead = 4

                try:
                    rxData = binho.i2c.read(targetDeviceAddress, bytesToRead)
                    #print(rxData)

                except BinhoException:
                    print("I2C Read Transaction failed!")


                # The data is a byte array, which is easy to work with programmatically, but if you'd like to
                # print it to the console in a more human-friendly format, try this
                # rcvdBytes = "Read {} byte(s):\t".format(len(rxData))
                # for byte in rxData:
                #     rcvdBytes += "\t " + "0x{:02x}".format(byte)

                # print(rcvdBytes)

                pressure_raw = float((rxData[0] << 8) | rxData[1])
                #print(type(pressure_raw))
                pressure_kpa = ((pressure_raw - 3277.0) * 7.63*10**(-6)) - 0.1  #from manual
                pressure_pa = pressure_kpa*1000

                temperature_raw = ((rxData[2] << 8) | rxData[3])

                # Output the running average and standrad deviation of the pressure in pascals
                data.append(pressure_pa)
                runningAverage = sum(data)/len(data)
                standardDeviation = np.std(data)
                print ("Time: %.2f" %(time.time() - timeout_start))
                print ("Differential Pressure: %.2f Pa" %(pressure_pa))
                print ("Running average and standard deviation: %.2f Pa %.2f Pa" %(runningAverage,standardDeviation), "\n")

                # Write data to CSV file
                timestamp_now = datetime.datetime.now()
                row_contents = [timestamp_now, pressure_raw, pressure_pa, temperature_raw]

                with open(filename, 'a+', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(row_contents)

                print(datetime.datetime.now())
                print("pressure raw = {}, pressure actual = {} Pa, temperature raw = {}".format(pressure_raw, pressure_pa, temperature_raw))

                timeout_start = time.time()

    except BinhoException:
        print("ReadRegister failed!")


    print("Finished!")

finally:

    # close the connection to the host adapter
    binho.close()
