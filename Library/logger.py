import asyncio
from Library.influxDB import influxDB
from Library.debug import logging

class logger:
    def __init__(self):
        # メンバ変数
        self.__DB1 = None
        self.__DB2 = None
        self.task = None

    async def start(self, data_func, DB1, DB2,save_db,delete_db):
        self.__save_db = save_db
        self.__delete_db = delete_db
        db1_flg = False
        db2_flg = False
        
        if self.__save_db == "-L": # loggingのみ保存
            self.__DB1 = influxDB(DB1.host, DB1.port, DB1.database, DB1.measurement)
            db1_flg = True
        elif self.__save_db == "-A":# 集約DBのみ保存
            self.__DB2 = influxDB(DB2.host, DB2.port, DB2.database, DB2.measurement)
            db2_flg = True
        elif self.__save_db == "-AL":# 両方保存
            self.__DB1 = influxDB(DB1.host, DB1.port, DB1.database, DB1.measurement)
            self.__DB2 = influxDB(DB2.host, DB2.port, DB2.database, DB2.measurement)
            db1_flg = True
            db2_flg = True
        elif self.__save_db == "-LA":# 両方保存
            self.__DB1 = influxDB(DB1.host, DB1.port, DB1.database, DB1.measurement)
            self.__DB2 = influxDB(DB2.host, DB2.port, DB2.database, DB2.measurement)
            db1_flg = True
            db2_flg = True
        elif self.__save_db == "-N":# 両方とも削除しない
            self.__DB1 = influxDB(DB1.host, DB1.port, DB1.database, DB1.measurement)
            self.__DB2 = influxDB(DB2.host, DB2.port, DB2.database, DB2.measurement)
            db1_flg = True
            db2_flg = True

        if db1_flg==False:
            if self.__delete_db == "-DL":
                self.__DB1 = influxDB(DB1.host, DB1.port, DB1.database, DB1.measurement)
            elif self.__delete_db == "-DLA":
                 self.__DB1 = influxDB(DB1.host, DB1.port, DB1.database, DB1.measurement)
            elif self.__delete_db == "-DLA":
                 self.__DB1 = influxDB(DB1.host, DB1.port, DB1.database, DB1.measurement)
        if db2_flg==False:
            if self.__delete_db == "-DA":
                self.__DB1 = influxDB(DB1.host, DB1.port, DB1.database, DB1.measurement)
            elif self.__delete_db == "-DLA":
                 self.__DB1 = influxDB(DB1.host, DB1.port, DB1.database, DB1.measurement)
            elif self.__delete_db == "-DLA":
                 self.__DB1 = influxDB(DB1.host, DB1.port, DB1.database, DB1.measurement)


        self.task = asyncio.create_task(self._work(data_func))
        
        
        

    async def stop(self):
        #print("------stop--------")
        if(self.task):
            self.task.cancel()
            await asyncio.gather(self.task, return_exceptions=True)
            logging.info("Data processing task cancelled successfully")
            self.task = None


    async def _work(self, data_func):
        #print("------_work--------")
        if self.__delete_db == "-DL":
            self.__DB1.delete()
        elif self.__delete_db == "-DA":
            self.__DB2.delete()
        elif self.__delete_db == "-DAL":
            self.__DB1.delete()
            self.__DB2.delete()
        elif self.__delete_db == "-DLA":
            self.__DB1.delete()
            self.__DB2.delete()
        
        try:
            while True:
                try:
                    tags, fields = data_func()
                    if tags and fields:
                        if self.__save_db == "-L": # loggingのみ保存
                            self.__DB1.write(tags, fields)
                        elif self.__save_db == "-A":# 集約DBのみ保存
                            self.__DB2.write(tags, fields)
                        elif self.__save_db == "-AL":# 両方保存
                            self.__DB1.write(tags, fields)
                            self.__DB2.write(tags, fields)
                        elif self.__save_db == "-LA":# 両方保存
                            self.__DB1.write(tags, fields)
                            self.__DB2.write(tags, fields)
                    await asyncio.sleep(0.1)
                except Exception as e:
                    logging.error(f"Error work: {e}")
                    pass
        except asyncio.CancelledError:
            logging.info("DB processing was cancelled.")
        except Exception as e:
            logging.error(f"Error Exception: {e}")

