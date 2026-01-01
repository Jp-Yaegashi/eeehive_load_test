

# 1. 環境構築

## 1-0. USBシリアルポート設定

まず、USB シリアルデバイス情報を確認します。

```bash
udevadm info -q all -n /dev/ttyUSB0
```

実行例：

```text
P: /devices/pci0000:00/0000:00:08.3/0000:67:00.0/usb3/3-2/3-2:1.0/ttyUSB0/tty/ttyUSB0
M: ttyUSB0
R: 0
U: tty
D: c 188:0
N: ttyUSB0
L: 0
S: serial/by-path/pci-0000:67:00.0-usb-0:2:1.0-port0
S: serial/by-path/pci-0000:67:00.0-usbv2-0:2:1.0-port0
S: serial/by-id/usb-FTDI_FT230X_Basic_UART_DQ01KCDT-if00-port0
E: DEVPATH=/devices/pci0000:00/0000:00:08.3/0000:67:00.0/usb3/3-2/3-2:1.0/ttyUSB0/tty/ttyUSB0
E: DEVNAME=/dev/ttyUSB0
E: MAJOR=188
E: MINOR=0
E: SUBSYSTEM=tty
E: USEC_INITIALIZED=202651379
E: ID_BUS=usb
E: ID_MODEL=FT230X_Basic_UART
E: ID_MODEL_ENC=FT230X\x20Basic\x20UART
E: ID_MODEL_ID=6015
E: ID_SERIAL=FTDI_FT230X_Basic_UART_DQ01KCDT
E: ID_SERIAL_SHORT=DQ01KCDT
E: ID_VENDOR=FTDI
E: ID_VENDOR_ENC=FTDI
E: ID_VENDOR_ID=0403
E: ID_REVISION=1000
E: ID_TYPE=generic
E: ID_USB_MODEL=FT230X_Basic_UART
E: ID_USB_MODEL_ENC=FT230X\x20Basic\x20UART
E: ID_USB_MODEL_ID=6015
```

### メモしておく値

後ほど以下の値を使用するため、**必ずメモ**してください。

* `SUBSYSTEM`
* `ID_SERIAL_SHORT`

上記の例では次の値になります。

* `SUBSYSTEM`：`tty`
* `ID_SERIAL_SHORT`：`DQ01K7UO`

---

### udev ルールファイルの作成

```bash
sudo nano /etc/udev/rules.d/99-usb-serial.rules
```

内容：

```text
SUBSYSTEM=="tty",ENV{ID_SERIAL_SHORT}=="DQ01K7UO",SYMLINK+="tty-2d1",MODE="0666"
```

### ルールの再読み込み

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
ls /dev/tty-2d1
```

---

## 1-1. ロギング部側

```bash
cd ~
git clone https://github.com/Jp-Yaegashi/eeehive_load_test.git
cd eeehive_load_test
echo 'source /home/log-1/venv/bin/activate' >> ~/.bashrc
. ~/.bashrc
```

---

## 1-2. 集約部側

```bash
cd ~
git clone https://github.com/Jp-Yaegashi/eeehive_load_test.git
cd eeehive_load_test
```

---

# 2. 環境構築後、本プログラムを実施したい場合

## 2-1. 集約部のサービスを全て停止

```bash
git fetch origin main
git reset --hard origin/main
sh stop_service.sh
```

---

## 2-2. ロギング部の負荷検証プログラム実行オプション

| No. | パラメータ  | 備考                |
| :-- | :----- | :---------------- |
| 1   | 数字     | 実施時間（分）           |
| 2   | `-DL`  | ロギング部の既存データ削除     |
| ^   | `-DA`  | 集約部の既存データ削除       |
| ^   | `-DLA` | ロギング部＆集約部の既存データ削除 |
| ^   | `-DAL` | ロギング部＆集約部の既存データ削除 |
| ^   | `-N`   | 既存データ削除しない        |
| 3   | `-L`   | ロギングDBに保存         |
| ^   | `-A`   | 集約部DBに保存          |
| ^   | `-LA`  | ロギング部＆集約部DBに保存    |
| ^   | `-AL`  | ロギング部＆集約部DBに保存    |

---

## 2-3. 既存データを削除せず、10分間ロギング部に保存

```bash
cd ~/eeehive_load_test
python3 test_program.py 10 -N -L
```

---

## 2-4. 既存データを削除せず、10分間集約部に保存

```bash
cd ~/eeehive_load_test
python3 test_program.py 10 -N -A
```

---

## 2-5. 既存データを削除せず、60分間ロギング部 & 集約部に保存

```bash
git reset --hard origin/main
python3 test_program.py 60 -N -LA
```

または

```bash
python3 test_program.py 60 -N -AL
```

---

## 2-6. 既存データ削除後、60分間ロギング部 & 集約部に保存

```bash
cd ~/eeehive_load_test
python3 test_program.py 60 -DAL -LA
```

または

```bash
python3 test_program.py 60 -DLA -AL
```

---

# 3. InfluxDB のデータ件数を確認

```bash
influx
use "eeeHiveSystemDB"
precision rfc3339
SELECT COUNT(*) FROM time_data_2d_table1
```

---

# 4. ディスク IO および CPU 使用率を確認（1秒間隔）

```bash
vmstat 1
```

* `wa`：ディスク IO 待ち時間

`vmstat` の CPU 項目（`us`, `sy`, `id`, `wa`, `st`）の合計は **100%** になります。

* **CPU使用率（%）**

  ```
  100 - id
  ```

---

## 4-1. vmstat の出力に「時刻」を付ける

```bash
vmstat 1 | awk '{ print strftime("%Y/%m/%d %H:%M:%S"), $0 }'
```

