# 1. 環境構築

## 1-1. ロギング部側
```
cd ~
git clone https://github.com/Jp-Yaegashi/eeehive_load_test.git
cd eeehive_load_test
echo 'source /home/log-1/venv/bin/activate' >> ~/.bashrc
```
### 1-2. 集約部側
```
cd ~
git clone https://github.com/Jp-Yaegashi/eeehive_load_test.git
cd eeehive_load_test
```


# 2. 環境構築後、本プログラム実施したい場合
## 2-1. 集約部のサービス全て停止する
```
sh stop_service.sh
```

## 2-2. ロギング部の負荷検証プログラム実施

 | No. | パラメータ | 備考 |
|:---- |:---- |:---- |
| 1 | 数字 | 実施時間(分) |
| 2 | -DL | ロギング部の既存データ削除 |
| ^ | -DA | 集約部の既存データ削除 |
| ^ | -DLA | ロギング部＆集約部の既存データ削除 |
| ^ | -DAL | ロギング部＆集約部の既存データ削除 |
| ^ | -N | 既存データ削除しない |
| 3 | -L | ロギングDBに保存する |
|^ | -A | 集約部DBに保存する |
|^ | -LA | ロギング部&集約部DBに保存する |
|^ | -AL  | ロギング部&集約部DBに保存する |

## 2-3. ロギング部 & 集約部　既存データを削除せず、<br>10分間タグ検知データをロギング部に保存したい場合
```
cd ~/eeehive_load_test
python3  test_program.py 10 -N -L
```

## 2-4. ロギング部 & 集約部　既存データを削除せず、<br>10分間タグ検知データを集約部に保存したい場合
```
cd ~/eeehive_load_test
python3  test_program.py 10 -N -A
```

## 2-5. ロギング部 & 集約部　既存データを削除せず、<br>60分間タグ検知データをロギング部 & 集約部に保存したい場合
```
cd ~/eeehive_load_test
python3  test_program.py 60 -N -LA
or 
python3  test_program.py 60 -N -AL

```


## 2-6. ロギング部 & 集約部　既存データを削除後、<br>60分間タグ検知データをロギング部 & 集約部に保存したい場合
```
cd ~/eeehive_load_test
python3  test_program.py 60 -DAL -LA
or 
python3  test_program.py 60 -DLA -AL

```


# 3. influx データ件数を確認したい
```
influx
use "eeeHiveSystemDB"
precision rfc3339
SELECT COUNT(*) FROM time_data_2d_table1
```

# 4. ディスクIO及びCPU使用率を確認したい(1秒間隔で確認)
```
vmstat 1
```
wa:  ディスクIO

vmstatコマンドの結果のcpuの項目（us、sy、id、wa、st）を足すと100になります。

CPU使用率（%）:100 － idの値

## 4-1. vmstatコマンドの実行結果に「時刻」を付けて表示させる場合
```
vmstat 1 | awk '{ print strftime("%Y/%m/%d %H:%M:%S"), $0 }'
```
