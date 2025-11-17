import requests
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError, InfluxDBServerError
from datetime import datetime, timezone
from Library.debug import logging

class influxDB:
    def __init__(self, host, port, database, measurement):
        # メンバ変数
        self.__client = InfluxDBClient(host, port, database=database, timeout=1)
        self.__measurement = measurement

        # 接続確認
        try:
            self.__client.ping()
        except (InfluxDBClientError, InfluxDBServerError, requests.exceptions.ConnectionError) as e:
            logging.error(f"Error connecting to InfluxDB: {e}")
            self.__client = None

    def write(self, tags, fields):
        json_body = [
            {
                "measurement": self.__measurement,
                "time": int(datetime.now(timezone.utc).timestamp() * 1e9),
                "tags": tags,
                "fields": fields
            }
        ]
        logging.debug(json_body)
        #logging.debug(fields)
        try:
            self.__client.write_points(json_body, time_precision='n')
        except (InfluxDBClientError, InfluxDBServerError) as e:
            logging.error(f"Error writing to InfluxDB: {e}")
        except requests.exceptions.ConnectionError as e:
            logging.error(f"Connection error with InfluxDB: {e}")
        except Exception as e:
            logging.error(f"Unexpected error writing to InfluxDB: {e}")

    def delete(self):
        #print("delete")
        query = 'DELETE FROM ' + self.__measurement
        self.__client.query(query)

