
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
class MqttCallPolicy():
    def pop_publickey(n, e):
        rase = 65537
        rasm = int(n, 16)
        key = rsa.RSAPublicNumbers(rase, rasm).public_key(default_backend())
        pem = key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        print(pem.decode().split('-----')[2])
        return pem.decode().split('-----')[2]
    def changeCallStutus(self,callparams,mqtt):
        equipmentnumber = callparams.equipmentNumber
        enterfloor = callparams.enterfloornumber
        exitfloor = callparams.exitfloornumber
        callerstate = callparams.callerState
        curentFloor_ = mqtt.elevatorPosition[equipmentnumber]
        currentDoor = mqtt.elevatorDoor[equipmentnumber]
        if callerstate == "Enter":
            if enterfloor == curentFloor_ and (currentDoor == "Opened" or currentDoor == "Opening"):
                return "Exit", equipmentnumber
        elif callerstate == "":
            if enterfloor == curentFloor_ and (currentDoor == "Opened" or currentDoor == "Opening"):
                return "Enter", equipmentnumber
        else:
            return None,equipmentnumber

    def ChangeGoupIdCallStatus(callparams, mqtt,elevatorGroupMap):
        equipmentnumber = callparams.equipmentNumber
        enterfloor = callparams.enterfloornumber
        exitfloor = callparams.exitfloornumber
        callerstate = callparams.callerState
        # curentFloor_ = mqtt.elevatorPosition[equipmentnumber]
        # currentDoor = mqtt.elevatorDoor[equipmentnumber]
        groupId = callparams.elevatorGroupId
        elevatorNumber = elevatorGroupMap[groupId]
        if callerstate == "Enter":
            for number in elevatorNumber:

                if enterfloor == mqtt.elevatorPosition[number] and (
                        mqtt.elevatorDoor[number] == "Opened" or mqtt.elevatorDoor[number] == "Opening"):
                    return "Exit", number
        elif callerstate == "":
            for number in elevatorNumber:
                if enterfloor == mqtt.elevatorPosition[number] and (
                        mqtt.elevatorDoor[number] == "Opened" or mqtt.elevatorDoor[number] == "Opening"):
                    return "Enter", number
        else:
            return None,equipmentnumber