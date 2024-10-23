import serial
print(serial.VERSION)


# シリアルポートを開く
ser = serial.Serial(
    port='COM3',  # 使用しているポート名に変更 (WindowsではCOMポート、Linux/macOSでは/dev/ttyUSBxなど)
    baudrate=115200,  # ボーレート
    timeout=1  # タイムアウト（必要に応じて調整）
)

# バイナリデータの送受信
binary_data = b'\x02\x00\x55\x07\x14\x02\x00\x00\x00\x00\x02\x03\x79\x0D'  # ログに対応するデータ
# データを送信
ser.write(binary_data)

# データを受信（32バイトを読み取る場合）
response_3 = ser.read(32)  # 32バイト分のデータを受信
# 受信データを16進数形式で連続表示（空白なし）
hex_string = response_3.hex()  # 16進数の文字列に変換
print("Received data:", hex_string)

# ポートを閉じる
ser.close()
