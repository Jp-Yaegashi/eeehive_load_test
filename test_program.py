from _2D import _2D
import serial
import serial.tools.list_ports
import os
import socket
from pydantic import BaseModel
from typing import List, Tuple, Optional
from Library.conf_handler import conf_handler
import sys
import asyncio
import time

from Library.debug import logging

device = None

async def main():
    run_time = 0
    args = sys.argv
    
    if 5 <= len(args):
        if args[1].isnumeric():
            run_time = int(args[1]) #実施時間(分)
        else:
            print("実施時間パラメータエラー")
            sys.exit(1)
        
        log_out = args[2] #ログ出力ありなし
        db_init = args[3] #既存データ削除確認
        pra_db = args[4] #ローカルDBに保存確認

        config = conf_handler("_2D/_2D.conf")
        print("集約PC側のサービスを停止してください。")
        device = _2D(config)
        device._set_pra_run_time(run_time)
        if pra_db == "-L": # loggingのみ保存
            device._set_pra_db(pra_db)
        elif pra_db == "-A":# 集約DBのみ保存
            device._set_pra_db(pra_db)
        elif pra_db == "-AL":# 両方保存
            device._set_pra_db(pra_db)
        elif pra_db == "-LA":# 両方保存
            device._set_pra_db(pra_db)
        else:
            print('DBパラメータエラー')
            sys.exit(1)
       
        await device.reset()
        print("RESET コマンドが実行されました")

        #device.start()
        task = asyncio.create_task(device.start())
        # 他の処理
        await asyncio.sleep(run_time*60)  # メイン処理
        task.cancel()             # 必要に応じてキャンセル
        try:
            await task
        except asyncio.CancelledError:
            print("タスクはキャンセルされました")

        print("START コマンドが実行されました")
       

    else:
        print('パラメータエラー')
        sys.exit(1)


# データモデルの定義
class SerialPort(BaseModel):
    serial_port: Optional[str]
    position_id: Optional[str]

class SerialSettings(BaseModel):
    position_mode: Optional[str]
    serial_ports: List[SerialPort]

asyncio.run(main())
