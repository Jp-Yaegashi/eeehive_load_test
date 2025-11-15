import asyncio
from types import SimpleNamespace
from Library.debug import logging
from Library.conf_handler import conf_handler
from Library.serial_handler import serial_handler

class device:
    def __init__(self, config: conf_handler):
        # メンバ変数
        self._config = config

    async def get_ID(self, ser: serial_handler):
        ser.read(b'>')
        ser.write(b'id\r')
        await asyncio.sleep(0.5)
        try:
            if ser.ser.in_waiting > 0:
                str = ser.read(b'\r').decode()
                if str.startswith("Board ID ="):
                    ID = str.split("=")[-1].strip()
                    logging.info(f"Reader ID for port {ser.port}: {ID}")
                    return ID
                elif str.startswith("Board ID :"):
                    ID = str.split(":")[-1].strip()
                    logging.info(f"Reader ID for port {ser.port}: {ID}")
                    return ID
                else:
                    logging.error(f"Unexpected response for Reader ID: {str}")
                    raise RuntimeError(f"Error getID")
            else:
                raise RuntimeError(f"Error getID")

        except Exception as e:
            logging.error(f"Error sending id command: {e}")
            raise RuntimeError(f"Error getID: {e}")
        
    def get_DB_conf(self):
        DB1 = SimpleNamespace(
            host        = self._config.get("influxdb1", "host").strip(), 
            port        = int(self._config.get("influxdb1", "port")), 
            database    = self._config.get("influxdb1", "database").strip(),
            measurement = self._config.get("influxdb1", "measurement").strip()
        )
        DB2 = SimpleNamespace(
            host        = self._config.get("influxdb2", "host").strip(), 
            port        = int(self._config.get("influxdb2", "port")), 
            database    = self._config.get("influxdb2", "database").strip(),
            measurement = self._config.get("influxdb2", "measurement").strip()
        )
        return DB1, DB2


    

        
