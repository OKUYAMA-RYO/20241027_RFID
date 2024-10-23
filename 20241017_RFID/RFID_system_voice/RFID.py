import serial
import os
import pandas as pd
import keyboard
import time
import binascii
from datetime import datetime
import pyttsx3  # 追加：音声読み上げライブラリ

# RFIDからの受信データに対する一回の読み取りビットの設定
READ_BYTE = 32

# 在庫管理ファイルパスの指定
csv_file = "./warehouse_database.csv"

# 在庫管理データベースの初期化
df = pd.DataFrame()

# pyttsx3エンジンを初期化
engine = pyttsx3.init()

# 音声で読み上げる関数
def speak(text):
    engine.say(text)
    engine.runAndWait()

# RFIDに読み取り命令を送る関数
def RFIDread(serial):
    binary_data = b'\x02\x00\x55\x07\x14\x02\x00\x00\x00\x00\x02\x03\x79\x0D'
    serial.write(binary_data)

# 受信データの読み取り関数
def serialReadLines(serial):
    received_data_list = []
    while True:
        received_data = serial.read(READ_BYTE)
        hex_data = binascii.hexlify(received_data).decode("utf-8")

        if received_data and len(hex_data) == 64:
            received_data_list.append(hex_data[22:46])  # 商品IDを抽出
            print("Received Data:", hex_data)
        else:
            print("LIST:")
            print(received_data_list)
            return received_data_list

# CSVファイルが存在するか確認
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
    print("CSVファイルを読み込みました。")
else:
    # 新しいデータベースを作成（previous_exsistenceを追加）
    data = {
        'ID': [],
        'exsistence': [],
        'previous_exsistence': [],  # 追加: 前回のフラグ状態
        'timestamp': []
    }
    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)
    df.to_csv(csv_file, index=False)
    print("新しいCSVファイルを作成しました。")

# シリアルポートを開く
ser = serial.Serial(
    port='COM3',
    baudrate=115200,
    timeout=1
)

while True:
    print("READ")

    # 1. 現在の exsistence フラグを previous_exsistence にコピー
    df['previous_exsistence'] = df['exsistence']

    # RFIDリーダーからデータを読み取る
    RFIDread(ser)
    rcv_data_list = serialReadLines(ser)

    # 2. すべての exsistence を False に設定し、読み取ったデータを True に設定
    df['exsistence'] = False
    for rcv_data in rcv_data_list:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        check_str = df[df["ID"].isin([rcv_data])]

        if check_str.empty:
            # 新しいタグの場合、True に設定して追加
            new_data = pd.DataFrame({
                "ID": [rcv_data],
                "exsistence": [True],
                "previous_exsistence": [False],  # 初期値は False
                "timestamp": [current_time]
            })
            df = pd.concat([df, new_data], ignore_index=True)
            print("ID: " + rcv_data + " をデータベースに登録しました（時間：" + current_time + "）。")
        else:
            # 既存のタグの場合、True に設定
            df.loc[df["ID"] == rcv_data, ["exsistence", "timestamp"]] = [True, current_time]

    # 3. previous_exsistence と exsistence を比較して、状態が変わった場合に音声で通知
    for index, row in df.iterrows():
        if row['previous_exsistence'] == True and row['exsistence'] == False:
            print(f"ID: {row['ID']} を貸し出しました（時間：{row['timestamp']}）。")
            speak(row['ID'][-4:] + "が貸し出しされました")
        elif row['previous_exsistence'] == False and row['exsistence'] == True:
            print(f"ID: {row['ID']} を返却しました（時間：{row['timestamp']}）。")
            speak(row['ID'][-4:] + "が返却されました")

    # CSVファイルを更新
    df.to_csv(csv_file, index=False)

    # ESCキーが押されたかチェック
    if keyboard.is_pressed('esc'):
        print("ESC キーが押されました。プログラムを終了します。")
        break

    time.sleep(5)

ser.close()
