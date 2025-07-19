import subprocess
import usb.core
import socket
import threading
import ast
import array

VID = 0x0b05
PID = 0x183c
HOST = '127.0.0.1'
PORT = 65432

dev = usb.core.find(idVendor=VID, idProduct=PID)
if dev is None:
    raise ValueError("Устройство не найдено")

try:
    if dev.is_kernel_driver_active(4):
        dev.detach_kernel_driver(4)

except Exception as e:
    print(f"Не удалось отсоединить драйвер ядра: {e}")

def get_volume():
    try:
        result = subprocess.run(['pactl', 'get-sink-volume', '@DEFAULT_SINK@'],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)

        if result.returncode == 0:
            output = result.stdout.strip()
            left_volume = output.split()[4]
            right_volume = output.split()[11]
            return left_volume, right_volume
        else:
            print(f"Ошибка: {result.stderr.strip()}")
            return None

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None

def set_volume(status):
    volume = get_volume()
    left_volume = int(volume[0].replace('%', ''))
    sink = "alsa_output.usb-ASUS_Xonar_U7_MKII-00.analog-stereo"
    if status == 0:
        subprocess.run(['pactl', 'set-sink-volume', sink, f'{volume[1]}', f'{volume[1]}'])
    else:
        subprocess.run(['pactl', 'set-sink-volume', sink, f'{left_volume + 13}%', f'{volume[1]}'])

def toggle(data):
    if data[10] == 48:
        set_volume(0)
        subprocess.run(['notify-send', 'Переключение на наушники'])
    elif data[10] == 160:
        set_volume(1)
        subprocess.run(['notify-send', 'Переключение на динамики'])

def handle_client(conn, addr):
    print(f"Connected by {addr}")
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            command = data.decode().strip()
            print(f"Received command: {command}")

            if command == "change":
                change_output()

def data_strip():
    with open("data", "r") as file:
        data_write = file.read().strip()

    if data_write.startswith("array(") and data_write.endswith(")"):
        inner = data_write[len("array("):-1]

        typecode_str, list_str = inner.split(',', 1)
        typecode = ast.literal_eval(typecode_str.strip())
        values = ast.literal_eval(list_str.strip())
        data_write = array.array(typecode, values)
        return data_write
    else:
        raise ValueError("Неправильный формат файла")

def change_output():
    data_write = data_strip()
    if data_write[10] == 160:
        data_write[10] = 48
        toggle(data_write)
    else:
        data_write[10] = 160
        toggle(data_write)

    bmRequestType = 0x21
    bRequest = 0x09
    wValue = (2 << 8) | 0
    wIndex = 4
    dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data_write)

    with open('data', 'w') as file:
        file.write(str(data_write))

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Daemon listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == '__main__':
    main()
