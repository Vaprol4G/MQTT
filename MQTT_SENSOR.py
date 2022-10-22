from operator import ne
import serial, serial.tools.list_ports
import paho.mqtt.client as mqtt_client
import time, random
import numpy as np


def connect():
    print("Ports list:")
    ports = []
    for elem in serial.tools.list_ports.comports():
        print(str(elem).split(' ')[0])
        ports += [str(elem).split(' ')[0]]

    port = "COM" + input("Enter COM port:")
    if port not in ports:
        print(f"Port {port} in not exists!")
        return -1

    s = serial.Serial(port=port, baudrate=9600)
    if not s.is_open:
        print(f"Connection failure!")
        return -2

    return s


def map(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


broker = "broker.emqx.io"
UNIQUE_ID = 589123456903456

client = mqtt_client.Client(f'lab_{random.randint(10000, 999999)}')

client.connect(broker)

arduino = serial.Serial(port="COM6", baudrate=9600)
# arduino = connect()

print("""Список команд:
1 - Получить моментальное значение сенсора
2 - Получить усредненное значение по 100 последним элементам
3 - Реализация потоковой передачи данных (default duration 20 seconds)
""")

duration = 20
queue = []
avg_value = 0
need_input = True

while True:
    if need_input:
        command = int(input("\rВведите номер команды: "))

    if (command == 3):
        temp = input("Введите продолжительность в секундах (enter for old value): ")
        if temp != '':
            duration = int(temp)
    elif command == 0:
        break

    arduino.write(np.array([1], dtype='uint8').tobytes())

    time.sleep(0.01)

    while arduino.inWaiting() < 2:
        print("\rWaiting data", end="")

    response = arduino.read(2)
    response = [int(byte_) for byte_ in response]
    response = (response[0] << 8 & 0xFF00) + (response[1] & 0xFF)
    response = map(response, 0, 1024, 0, 100)
    queue = [response] + queue
    avg_value += response
    if len(queue) >= 100:
        avg_value -= queue.pop()

    if command == 1:
        client.publish(f'lab/{UNIQUE_ID}/photo/instant', response)
    elif command == 2:
        client.publish(f'lab/{UNIQUE_ID}/photo/average', avg_value / len(queue))
    elif command == 3:
        need_input = False
        timer_start = time.time()
        command = 4
    elif command == 4:
        print("\rSending data", end="")
        if time.time() - timer_start >= duration:
            need_input = True
        client.publish(f'lab/{UNIQUE_ID}/photo/stream', response)
        time.sleep(0.1)

print("Disconnect!")
client.disconnect()
