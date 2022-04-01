import multiprocessing
import os
import sys
import time

import serial


class SerialProcess(multiprocessing.Process):

    def __init__(self, input_queue, output_queue, serial_port, baud_rate, timeout):
        multiprocessing.Process.__init__(self)
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.sp = serial.Serial(serial_port, baud_rate, timeout=timeout)

    def close(self):
        self.sp.close()

    def write_serial(self, data):
        cmd = data + '\r'
        self.sp.write(cmd.encode())
        # time.sleep(1)

    def read_serial(self):
        try:
            ret = self.sp.readline().decode().rstrip().replace('\r', '<br>')
        except serial.serialutil.SerialException:
            print('ERROR: Serial device disconnected or multiple access on port?')
            print('       Press Ctrl+C to exit')
            raise

        return ret

    def run(self):
        self.sp.flushInput()
        while True:
            # look for incoming tornado request
            if not self.input_queue.empty():
                data = self.input_queue.get()

                # send it to the serial device
                self.write_serial(data)
                print("write: " + data)

            # look for incoming serial data
            if (self.sp.inWaiting() > 0):
                try:
                    data = self.read_serial()
                except:
                    break
                print("read: " + data)
                # send it back to tornado
                self.output_queue.put(data)
