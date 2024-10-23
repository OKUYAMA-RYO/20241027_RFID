import serial
import time
import binascii

# RFIDからの受信データに対する一回の読み取りビットの設定
READ_BYTE = 32

# RFIDに読み取り命令を送る関数
def RFIDread(serial):
    # 送信するバイナリデータ（読み取り命令）
    binary_data = b'\x02\x00\x55\x07\x14\x02\x00\x00\x00\x00\x02\x03\x79\x0D'
    # データを送信
    serial.write(binary_data)

# 受信データの全てを読み取る関数
def serialReadLines(serial):
    received_data_list = []
    while True:
        # データを受信
        received_data = serial.read(READ_BYTE)  # 最大[READ_BYTE]バイトまでのデータを受信
        hex_data = binascii.hexlify(received_data).decode("utf-8")

        if received_data and len(hex_data) == 64:  # 読み込んだデータが32バイトの時
            received_data_list.append(hex_data[22:46])  # 商品IDのみを抽出してリストに追加
            print("Received Data:", hex_data)
        
        else:  # データがなくなったら終了
            print("LIST:")
            print(received_data_list)
            return received_data_list

# シリアルポートを開く
ser = serial.Serial(
    port='COM3',  # 使用しているポート名に変更
    baudrate=115200,  # ボーレート
    timeout=1  # タイムアウト（必要に応じて調整）
)

while True:
    print("READ")

    # RFIDへのREAD命令
    RFIDread(ser)

    # 受信データの読み取り
    rcv_data_list = serialReadLines(ser)

    # 受信したすべてのタグIDを出力
    for rcv_data in rcv_data_list:
        print("Received Tag ID: " + rcv_data)
    
    # 1秒待機（調整可能）
    time.sleep(1)

# ポートを閉じる
ser.close()
