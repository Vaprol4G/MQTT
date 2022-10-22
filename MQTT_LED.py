import paho.mqtt.client as mqtt_client
import random
import time
import serial

DELTA = 3
THRESHOLD = 5
queue = [0]
min_value = 100
max_value = 0


def action_1(client, data, message):
    global queue

    data = float(message.payload.decode("utf-8"))

    if len(queue) >= 4:
        queue.pop()

    avg = (max(queue) + min(queue)) / 2
    d_avg_min = avg - DELTA
    d_avg_max = avg + DELTA

    if data < d_avg_min:
        ser.write("1".encode())
    elif data > d_avg_max:
        ser.write("0".encode())

    queue = [data] + queue

    return data


def action_2(client, data, message):
    global min_value
    global max_value

    data = float(message.payload.decode("utf-8"))

    if data > max_value:
        max_value = data
    elif data < min_value:
        min_value = data

    avg = (max_value + min_value) / 2

    if data > avg:
        ser.write("1".encode())
    else:
        ser.write("0".encode())

    return data


print("""Доступно 2 режима работы:
1 - нахождение убывающих и возрастающих участков рядов измерений. (светодиод светиться на участках убывающей яркости)
2 - включение и выключение по порогу освещенности""")

UNIQUE_ID = 589123456903456
port = "COM7"
ser = serial.Serial(port, 9600)

broker = "broker.emqx.io"

client = mqtt_client.Client(f"lab_{random.randint(10000, 99999)}")

mode = 0
mode = int(input("Enter working mode: "))
if mode == 1:
    client.on_message = action_1
elif mode == 2:
    client.on_message = action_2
else:
    raise ("Wrong working mode")

try:
    client.connect(broker)
except Exception:
    print("Failed to connect. Check network")
    exit()

client.loop_start()

print("Subscribing")

client.subscribe(f'lab/{UNIQUE_ID}/photo/instant')
client.subscribe(f'lab/{UNIQUE_ID}/photo/average')
client.subscribe(f'lab/{UNIQUE_ID}/photo/stream')

time.sleep(600)

client.disconnect()
client.loop_stop()
print("Stop communication")
