import multiprocessing
import os
import sys
import time

import serial

# Change this to match your local settings
SERIAL_PORT = '/dev/ttyS0'
SERIAL_BAUDRATE = 115200


class SerialProcess(multiprocessing.Process):

    def __init__(self, input_queue, output_queue):
        multiprocessing.Process.__init__(self)
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.sp = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=1)

    def close(self):
        self.sp.close()

    def writeSerial(self, data):
        cmd = data + '\r'
        self.sp.write(cmd.encode())
        # time.sleep(1)

    def readSerial(self):
        try:
            ret = self.sp.readline().decode().rstrip().replace('\r', '\n')
            #ret = ret.replace('\r\n', '\n').replace(
            #    '\r', '\n').replace('\n\n', '\n').replace('\r\r', '\n')
        except serial.serialutil.SerialException:
            print('ERROR: serial device disconnected or multiple access on port?')
            os._exit(os.EX_OK)

        return ret

    def run(self):

        self.sp.flushInput()

        while True:
            # look for incoming tornado request
            if not self.input_queue.empty():
                data = self.input_queue.get()

                # send it to the serial device
                self.writeSerial(data)
                print("write: " + data)

            # look for incoming serial data
            if (self.sp.inWaiting() > 0):
                data = self.readSerial()
                print("read: " + data)
                # send it back to tornado
                self.output_queue.put(data)
