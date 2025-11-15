import configparser
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Tuple, Optional
import serial
import serial.tools.list_ports
import os
import socket
from _2D import _2D
from FLEX import FLEX
from SENS import SENS
from Library.debug import logging
from Library.conf_handler import conf_handler

import asyncio

app = FastAPI()

# CORS設定 
origins = [ 
    "http://localhost:3000", # GrafanaのURL 
    "http://10.17.10.1:3000",
    "http://10.17.10.2:3000"
] 
#origins = ["*"]

app.add_middleware( 
    CORSMiddleware, 
    allow_origins=origins, 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 設定の読み込み
config = conf_handler("device_type.conf")
device_type = config.get("DEVICE","device_type")

# デバイスタイプに応じた処理モジュールのインポート
device = None
config_file_path = None
if device_type == "2D":
    config = conf_handler("_2D/_2D.conf")
    device = _2D(config)
elif device_type == "FLEX":
    config = conf_handler("FLEX/FLEX.conf")
    device = FLEX(config)
elif device_type == "SENS":
    config = conf_handler("SENS/SENS.conf")
    device = SENS(config)
else:
    raise Exception("Unknown device type (valid types: 2D, FLEX, SENS)")

# 測定開始コマンド
@app.post("/start")
async def start_endpoint():
    await device.start()
    return JSONResponse({"message": "START コマンドが実行されました"})

# 測定終了コマンド
@app.post("/stop")
async def stop_endpoint():
    await device.stop()
    return JSONResponse({"message": "STOP コマンドが実行されました"})

# 測定終了コマンド
@app.post("/reset")
async def reset_endpoint():
    await device.reset()
    return JSONResponse({"message": "RESET コマンドが実行されました"})

@app.post("/reboot")
async def reboot():
    os.system("sudo reboot")
    return {"status": "reboot"}

@app.post("/shutdown")
async def shutdown():
    os.system("sudo shutdown -h now")
    return {"status": "Shutting down"}

@app.get("/")
async def index(request: Request):
    hostname = socket.gethostname()  # ホスト名を取得
    return templates.TemplateResponse("index.html", {"request": request, "hostname": hostname, "device_type": device_type})

@app.get("/setting")
async def get_settings(request: Request):
    hostname = socket.gethostname()  # ホスト名を取得
    available_ports = []
    ports = [port.device for port in serial.tools.list_ports.comports()]
    serials: List[Tuple[str, serial.Serial]] = []

    # シリアルポートを開く
    for port in ports:
        try:
            ser = serial.Serial(port, 115200, timeout=1)
            serials.append((port, ser))
        except Exception as e:
            continue

    # ID取得コマンドを送信
    for port, ser in serials:
        try:
            if device_type == "SENS":
                ser.write(b'\r')
                await asyncio.sleep(0.1)
            ser.read_until(b'>')  # プロンプトの終了文字を待つ
            ser.write(b'id\r')    # ID取得コマンドを送信
        except Exception as e:
            logging.error(f"Error sending id command to port {port}: {e}")

    await asyncio.sleep(0.5)

    # 受信データを確認
    for port, ser in serials:
        try:
            if ser.in_waiting > 0:
                response = ser.read_until(b'\r').decode().strip()
                if response.startswith("Board ID ="):
                    reader_id = response.split("=")[-1].strip()
                    available_ports.append({"port": port, "reader_id": reader_id})
                elif response.startswith("Board ID :"):
                    reader_id = response.split(":")[-1].strip()
                    available_ports.append({"port": port, "reader_id": reader_id})
        except Exception as e:
            logging.error(f"Error reading from port {port}: {e}")
        finally:
            ser.close()  # シリアルポートを閉じる

    return templates.TemplateResponse("setting.html", {"request": request, "hostname": hostname, "device_type": device_type, "ports": available_ports})


# データモデルの定義
class SerialPort(BaseModel):
    serial_port: Optional[str]
    position_id: Optional[str]

class SerialSettings(BaseModel):
    position_mode: Optional[str]
    serial_ports: List[SerialPort]

# SERIAL設定の上書き用API
@app.post("/save_setting")
async def save_setting(serial_settings: SerialSettings):
    logging.info(f"Received data: {serial_settings}")
    if device_type == "2D":
        # SERIAL1〜4の設定を更新
        for i, serial_data in enumerate(serial_settings.serial_ports, start=1):
            serial_key = f"SERIAL{i}"
            if serial_data.serial_port:
                config.set(serial_key,'enabled','True')
                config.set(serial_key,'serial_port',serial_data.serial_port)
                config.set(serial_key,'position_id',serial_data.position_id)
            else:
                config.set(serial_key,'enabled','False')
            # その他の固定設定
            config.set(serial_key,'baud_rate','115200')
            config.set(serial_key,'timeout','1')
    else:
        config.set("SERIAL",'serial_port',serial_settings.serial_ports[0].serial_port)
        config.set("SERIAL",'baud_rate','115200')
        config.set("SERIAL",'timeout','1')

    return {"message": "設定ファイルが正常に更新されました"}
