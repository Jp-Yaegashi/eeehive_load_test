
import serial
from Library.debug import logging

class serial_handler:
    def __init__(self):
        # メンバ変数
        self.ser = None
        self.port = None

    def open(self, port, baud_rate, timeout):
        try:
            self.port = port
            self.ser = serial.Serial(port, baud_rate, timeout = timeout)
            logging.info(f"Open serial connection  on {self.port}.")
        except serial.SerialException as e:
            print(f"Error open serial connection on {self.port}: {e}")
            logging.error(f"Error open serial connection on {self.port}: {e}")

    def close(self):
        try:
            self.ser.close()
            logging.info(f"Close serial connection on {self.port}.")
        except Exception as e:
            logging.error(f"Error close serial connection on {self.port}: {e}")

    def write(self, command: bytes):
        try:
            self.ser.write(command)
            logging.info(f"Write serial connection on {self.port} to {command}.")
        except Exception as e:
            logging.error(f"Error write serial connection on {self.port} to {command}: {e}")

    def read(self, until: bytes):
        try:
            if self.ser.in_waiting > 0:
                data = self.ser.read_until(until)
                return data
        except Exception as e:
            logging.error(f"Error read serial connection on {self.port}: {e}")
