import asyncio
import functools
from types import SimpleNamespace
from typing import List
from Library.debug import logging
from Library.device import device
from Library.serial_handler import serial_handler
from Library.logger import logger
from datetime import datetime

class _2D(device):
    def __init__(self, config):
        super().__init__(config)

        self.__sers: List[serial_handler] = []
        self.__position_ids = []
        self.__reader_ids = []
        self.__loggers: List[logger] = []
        #実施時間
        self.__run_time = 0
        self.__save_db = 0
        


    async def start(self):
        print("------start--------")
        print(self.__run_time)
        print(self.__save_db)
        if(self.__loggers):
            await self.stop()
            await asyncio.sleep(0.5)

        self._ser_open()
        DB1, DB2 = super().get_DB_conf()
        self.__reader_ids = await asyncio.gather(*[
            super().get_ID(ser) for ser in self.__sers
        ])

        await asyncio.gather(*[
            self.__run(ser) for ser in self.__sers
        ])

        self.__loggers.clear()
        for ser, reader_id, position_id in zip(self.__sers, self.__reader_ids, self.__position_ids):
            self.__loggers.append(logger())
            await self.__loggers[-1].start(functools.partial(self._make_2D_data, ser, reader_id, position_id), DB1, DB2,self.__run_time,self.__save_db)
        logging.debug(f"start_2D")
        now = datetime.now()
        print(now.strftime("%Y-%m-%d %H:%M:%S"))

        
    async def stop(self):
        for ser in self.__sers:
            ser.write(b's\r')
        for logger in self.__loggers:
            await logger.stop()
        for ser in self.__sers:
            ser.close()
        self.__loggers.clear()
        self.__sers.clear()
        self.__position_ids.clear()
        logging.debug(f"stop_2D")

    async def reset(self):
        print("------reset--------")
        print(self.__run_time)
        print(self.__save_db)
        if(self.__loggers):
            await self.stop()
            await asyncio.sleep(0.5)
        self._ser_open()
        for ser in self.__sers:
            ser.write(b'reset\r')
        await asyncio.sleep(6)
        for ser in self.__sers:
            ser.read(b'>')
        logging.debug(f"reset_2D")

    def _set_pra_run_time(self,run_time):
        print("------_set_pra_run_time--------")
        self.__run_time = run_time
        print(self.__run_time)
    
    def _set_pra_db(self,save_db):
        print("------_set_pra_db--------")
        self.__save_db = save_db
        print(self.__save_db)

    def _ser_open(self):
        self.__sers.clear()
        self.__position_ids.clear()
        #confファイルの読み込み
        for i in range(1, 5):
            section_name = f"SERIAL{i}" 
            if self._config.getboolean(section_name, "enabled"):
                port = self._config.get(section_name, "serial_port").strip()
                baud_rate = int(self._config.get(section_name, "baud_rate"))
                timeout = int(self._config.get(section_name, "timeout"))
                self.__position_ids.append(self._config.get(section_name, "position_id").strip())
                self.__sers.append(serial_handler())
                self.__sers[-1].open(port, baud_rate, timeout)


    async def __run(self, ser: serial_handler):
        ser.write(b'run\r')
        await asyncio.sleep(0.1)
        ser.read(b'>')


    def _make_2D_data(self, ser: serial_handler, reader_id, position_id):
        if not (ser.ser.is_open and ser.ser.in_waiting > 0):
            return None, None
        data = ser.read(b'\r').decode().strip()
        if not data:
            return None, None
        parsed_data = self.__parse_data(data)
        if not parsed_data:
            return None, None
        tag_spec_id, antenna_id, detected_tag_ids = parsed_data
        tags_json = {
            "position_id": position_id,
            "reader_id": reader_id,
            "tag_spec_id": int(tag_spec_id),
            "antenna_id": int(antenna_id)
        }
        fields_json = {
            **{f"detection_tag_{i+1}": tag for i, tag in enumerate(detected_tag_ids)}
        }
        return tags_json, fields_json


    def __parse_data(self, data):
        try:
            tag_spec_id, rest = data.split(',', 1)
            antenna_id, detected_tags = rest.split(':', 1)
            detected_tag_ids = [tag.strip() for tag in detected_tags.split(',')]
            return tag_spec_id.strip(), antenna_id.strip(), detected_tag_ids
        except ValueError:
            logging.error(f"Failed to parse data: {data}")
            return None



