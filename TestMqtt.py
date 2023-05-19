# python3.6

import random
from paho.mqtt import client as mqtt_client


broker = '116.236.153.190'	# 与Publish一样
port = 18001	# 与Publish一样
topic = "elevator/+/cabin/door/#"  # 准备订阅该Topic
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'	# 生成一个设备号


# 与小节3一直，都是连接到Borker
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


# 订阅函数，设定要订阅的Topic，以及设定接受信息后的回调函数
def subscribe(client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    client.subscribe("elevator/+/travel-direction")
    client.subscribe("elevator/+/cabin/position")
    client.subscribe("elevator/+/cabin/door/+/state")
    client.subscribe("elevator/+/cabin/load/actual-load")
    client.subscribe("elevator/+/cabin/load/actual-percentage")
    client.subscribe("elevator/+/cabin/load/overload")
    client.subscribe("elevator/+/floors/+/label")
    client.subscribe("elevator/+/state/mode")
    client.subscribe("cop_update/response/#")

    client.on_message = on_message

if __name__ == '__main__':
    client=connect_mqtt()
    subscribe(client)
    client.loop_forever()