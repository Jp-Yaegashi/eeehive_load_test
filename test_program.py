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
from datetime import datetime
from Library.debug import logging
import subprocess

device = None

def stop_service(service_name):
    try:
        subprocess.run(
            ["sudo", "systemctl", "stop", service_name],
            check=True
        )
        print(f"サービス '{service_name}' を停止しました。")
    except subprocess.CalledProcessError:
        print(f"サービス '{service_name}' の停止に失敗しました。")

async def main():
    run_time = 0
    args = sys.argv
    
    
    
    if 4 <= len(args):
        if args[1].isnumeric():
            run_time = int(args[1]) #実施時間(分)
        else:
            print("実施時間パラメータエラー")
            sys.exit(1)
        
        db_init = args[2] #既存データ削除確認
        pra_db = args[3] #ローカルDBに保存確認
        config = conf_handler("_2D/_2D.conf")
        device = _2D(config)

        if db_init == "-DL": # 既存DB削除
            device._set_pra_delete_db(db_init)
            print("---------ロギング部の既存データ削除します---------") 
            print("")
        elif db_init == "-DA":
            print("---------集約部の既存データ削除します---------") 
            print("")
            device._set_pra_delete_db(db_init)
        elif db_init == "-DLA": # 
            device._set_pra_delete_db(db_init)
            print("---------ロギング部＆集約部の既存データ削除します---------") 
            print("")
        elif db_init == "-DAL": # 既存DB削除
            device._set_pra_delete_db(db_init)
            print("---------ロギング部＆集約部の既存データ削除します---------") 
            print("")
        elif db_init == "-N":
            print("---------既存DBデータを削除しない---------") 
            print("")
            device._set_pra_delete_db(db_init)
        else:
            print('Error:既存DB削除パラメータエラー')
            sys.exit(1)


        if pra_db == "-L": # loggingのみ保存
            device._set_pra_db(pra_db)
            print("---------ロギングPCにタグ検知データを保存します---------")  
            print("")
        elif pra_db == "-A":# 集約DBのみ保存
            device._set_pra_db(pra_db)
            print("---------集約PCにタグ検知データを保存します---------")  
            print("")
        elif pra_db == "-AL":# 両方保存
            device._set_pra_db(pra_db)
            print("---------ロギングPCと集約PCにタグ検知データを保存します---------")  
            print("")
        elif pra_db == "-LA":# 両方保存
            device._set_pra_db(pra_db)
            print("---------ロギングPCと集約PCにタグ検知データを保存します---------")  
            print("")
        else:
            print('Error:DB保存パラメータエラー')
            sys.exit(1)

        stop_service("myapi")
        
        print("---------集約PC側のサービスを停止してください。---------")       
        await device.reset()
        
        print("")
        logging.info("---------タグ検証開始します---------") 
        now = datetime.now()
        print("\033[33m"+now.strftime("%Y-%m-%d %H:%M:%S") + ":---------タグ検証開始します---------\033[0m")
        print("")

        logging.info("---------処理実施時間："+ str(run_time) + "分") 
        print("---------処理実施時間：" + str(run_time) +"分---------")
        print("")

        
        task = asyncio.create_task(device.start())
        # 他の処理
        await asyncio.sleep(run_time*60)  # メイン処理
        task.cancel()             # 必要に応じてキャンセル
        try:
            await task
        except asyncio.CancelledError:
            print("タスクはキャンセルされました")
        
        logging.info("---------タグ検証終了しました---------") 
        now = datetime.now()
        print("\033[33m"+now.strftime("%Y-%m-%d %H:%M:%S") + ":---------タグ検証終了しました---------\033[0m")

    else:
        print('パラメータエラー')
        sys.exit(1)




asyncio.run(main())
