
import paho.mqtt.client as mqtt
import time
from paho.mqtt import client as mqtt_client
import json
import threading
class MqttClientUtil():

    def __init__(self):
        self.elevators = {}
        self.elevatorDiraction={}
        self.elevatorDoor={}
        self.elevatorMode={}
        self.elevatorfloors={}
        self.elevatorPosition={}
        # 必须设置，否则会返回「Connected with result code 4」
        #self.client = self.connect_mqtt()
        #self.subscribe(self.client)
        #self.client.loop_start()
        t1 = threading.Thread(target=self.task_thread)
        t1.start()
        #t2 = threading.Thread(target=self.task_chckMqtt)
        #t2.start()
    def task_chckMqtt(self):
        while True:
            isconnected=self.client.is_connected()
            if isconnected:
                pass
            else:
                self.client.loop_stop()
                self.client = self.connect_mqtt()
                self.subscribe(self.client)
                self.client.loop_start()
            time.sleep(5)


    def task_thread(self):
        self.client =self. connect_mqtt()
        self.subscribe(self.client)
        self.client.loop_forever()
    # 与小节3一直，都是连接到Borker
    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client("111")
        client.on_connect = on_connect
        client.connect("116.236.153.190", 18001)
        return client

    # 订阅函数，设定要订阅的Topic，以及设定接受信息后的回调函数
    def subscribe(self,client):
        def on_message(client, userdata, msg):



            topic=msg.topic
            if "travel-direction" in topic:

                dic_str = eval(msg.payload)


                query = dic_str
                equipment_number = query["Name"].split("=")[1].split("}")[0]
                print(equipment_number)
                value = query["Value"]
                self.elevatorDiraction[equipment_number]=value
                print("dir",self.elevatorDiraction)
            elif "cabin/position" in topic:
                equipment_number,value = self.xmlPase(str(msg.payload))

                self.elevatorPosition[equipment_number]=value
                print("pos", self.elevatorPosition)
            elif "cabin/door" in topic:
                dic_str = eval(msg.payload)


                query = dic_str
                equipment_number = query["Name"].split("=")[1].split("}")[0]
                value = query["Value"]
                self.elevatorDoor[equipment_number] = value
                print("door", self.elevatorDoor)

            elif "actual-load" in topic:
                pass
            elif "actual-percentage" in topic:
                pass
            elif "overload" in topic:
                pass
            elif "state/mode" in topic:
                dic_str = eval(msg.payload)


                query = dic_str
                equipment_number = query["Name"].split("=")[1].split("}")[0]
                value = query["Value"]
                self.elevatorMode[equipment_number] = value
                print("mode", self.elevatorMode)
            elif "floors" in topic:
                print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
                dic_str = eval(msg.payload)


                query = dic_str
                equipment_number = query["Name"].split("=")[1].split("}")[0]
                value = query["Value"]
                number_=[]
                if equipment_number in self.elevatorfloors:
                    number_ = self.elevatorfloors[equipment_number]
                    print(number_)
                else:
                    number_=[]
                number_.append(value)
                self.elevatorfloors[equipment_number] = number_
                print("floors", self.elevatorfloors)



        client.subscribe("elevator/+/travel-direction")
        client.subscribe("elevator/+/cabin/position")
        client.subscribe("elevator/+/cabin/door/+/state")
        client.subscribe("elevator/+/cabin/load/actual-load")
        client.subscribe("elevator/+/cabin/load/actual-percentage")
        client.subscribe("elevator/+/cabin/load/overload")
        client.subscribe("elevator/+/floors/+/label")
        client.subscribe("elevator/+/state/mode")

        client.on_message = on_message

    def xmlPase(self,payload):
        split = payload.split(",")

        Name = split[0][1:]

        Value = split[1]
        equipmentNumber=self.putName(Name)
        postion=self.putValue(Value)
        return equipmentNumber,postion


    def putName(self,Name):
        i = Name.index("{")


        p = Name.index("}")

        return Name[i + 1: p].split("=")[1]
    def putValue(self,Value):

        i = Value.index("{")

        p = Value.index("}")
        return Value[i + 1:p - 1].split(":")[1][1:]


    def start_sending_floor_call(self, elevator_id,label,floor,dir):
        ScheduleCall ="commands/floor-call"
        data={'TimeStamp':'867933050019185','Value':{'EquipmentNumber':elevator_id,'CallType':'Normal','Side':label
              ,'Direction':dir,'Floor':floor}}
        self.client.publish(ScheduleCall,json.dumps(data))



    def send_cabin_call(self, elevator_id,label,floor):
        ScheduleCall = "commands/cabin-call";
        data = {'TimeStamp': '867933050019185',
                'Value': {'EquipmentNumber': elevator_id, 'CallType': 'Normal', 'Side': label
                    , 'Deck': 'Lower', 'Floor': floor}}
        self.client.publish(ScheduleCall,json.dumps(data))
    def mqtt_isconnect(self):
        return  self.client.is_connected()



