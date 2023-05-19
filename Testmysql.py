from cryptography.hazmat.backends import default_backend
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import request
import base64
import rsa
import  time
import jwt
import uuid
from MqttClentUtil import MqttClientUtil
from MqttCallPolicy import MqttCallPolicy
import threading

from flask_jwt_extended import create_access_token
from gevent import pywsgi
import json

app = Flask(__name__,static_url_path='')
DIALECT = 'mysql'
DRIVER = 'mysqlconnector'
USERNAME = 'robot_api'
PASSWORD = 'Schindler2023'
HOST = 'rm-uf68x01f1cb0z44j5ao.mysql.rds.aliyuncs.com'
PORT = '3306'
DATABASE = 'schindler'


SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT, DRIVER, USERNAME, PASSWORD, HOST, PORT,
                                                                       DATABASE)
secret_key='MDk4ZjZiY2Q0NjIxZDM3M2NhZGU0ZTgzMjYyN2I0ZjY='
print(SQLALCHEMY_DATABASE_URI)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)
mqtt=MqttClientUtil()
elevatorTask={}
elevatorGroupMap={}



def task_hold_door():
    while True:
        for task in elevatorTask.keys():
            tupletask=elevatorTask[task]
            callStatus=tupletask['callStatus']
            equimentNumber=tupletask['equimentNumber']
            FirstTemp=tupletask['FirstTemp']
            FinalTemp=tupletask['FinalTemp']
            iscancel=tupletask['isCancel']
            enterFloorNum=tupletask['enterFloorNum']
            enterSide=tupletask['enterSide']
            exitFloorNum=tupletask['exitFloorNum']
            exitSide=tupletask['exitSide']
            currentTime=time.time()
            dir=mqtt.elevatorDiraction[task]
            if iscancel:
                #已经取消 不执行
                pass
            else:
                if currentTime-FinalTemp>1*30*1000 or FinalTemp-FirstTemp>5*60*1000:
                    elevatorTask.pop(task)
                else:
                    if callStatus=="Enter":
                        mqtt.start_sending_floor_call(task,enterSide,enterFloorNum,dir)
                    elif callStatus=="Exit":
                        if exitFloorNum==1:

                            mqtt.start_sending_floor_call(task, exitSide, exitFloorNum, "Up")
                        else:
                            if dir=="None":
                                mqtt.start_sending_floor_call(task, exitSide, exitFloorNum, "Down")
                            else:
                                mqtt.start_sending_floor_call(task, enterSide, enterFloorNum, dir)
        time.sleep(1)

t3 = threading.Thread(target=task_hold_door)
t3.start()







class Test_table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    quantity = db.Column(db.Integer)

class CallEquipmentNumber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipmentnumber = db.Column(db.String(50))
    userId = db.Column(db.String(50))

class Callpower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    certificateid = db.Column(db.String(50))
    equipmentid = db.Column(db.Integer)
    equipmentnumber = db.Column(db.String(50))

class Calllicense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    license = db.Column(db.String(50))
    nickname = db.Column(db.String(50))
    count=db.Column(db.Integer)

class Callcertificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Certificate = db.Column(db.String(500))
    publickey = db.Column(db.String(5000))
    nickename = db.Column(db.String(50))


class Calleleparams(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    callid = db.Column(db.Integer)
    maxweight = db.Column(db.String(50))
    enterfloornumber = db.Column(db.Integer)
    enterfloor = db.Column(db.String(50))
    equipmentNumber = db.Column(db.String(50))
    elevatorGroupId = db.Column(db.String(50))
    callStatus = db.Column(db.String(50))
    requestType = db.Column(db.String(50))
    exclusive = db.Column(db.String(50))
    callStatusReason = db.Column(db.String(50))
    exitfloornumber = db.Column(db.Integer)
    entersidelabel = db.Column(db.String(50))
    exitsidelabel = db.Column(db.String(50))
    callerState = db.Column(db.String(50))
    isCancel = db.Column(db.String(50))
    FirstTemp = db.Column(db.DateTime, default=datetime.utcnow)
    FinalTemp = db.Column(db.DateTime, default=datetime.utcnow)

# create a new data in table "stock"

with app.app_context():
    row_to_update = Test_table.query.filter_by(name='Apple11').first()
    print(row_to_update)



def getCerErrorMessage(str,error):
    return {"traceId": "","errors": [{ "message": str,"source": ""}]},error
@app.route('/certificates', methods=['POST'])
def certificates():
    # retrieve public key information from JSON payload

    print()
    data=request.json["deviceCertificate"]
    public_key = data['publickey']
    exponent = public_key['exponent']
    modulus = public_key['modulus']

    # retrieve authorization headers from request
    authorization = request.headers.get('Authorization')
    with app.app_context():
        re=Calllicense.query.filter_by(license=authorization).first()
        print(re.license)
        if re is None:
            return getCerErrorMessage("Not Find License",400)
        else:
            if re.count==0:
                cl=re.license+"schindlercall2022"
                base64_number = base64.b64encode(cl.encode('utf-8'))
                print(base64_number)

                rsaPublickey= MqttCallPolicy().pop_publickey(modulus,exponent)
                print(rsaPublickey)

                re.count=1
                new_stock = Callcertificate(Certificate=base64_number, publickey=rsaPublickey,nickename=re.nickname)
                db.session.add(new_stock)
                db.session.commit()

                return {'signedCertificate':base64_number},200
            else:
                return getCerErrorMessage("License used",400)

def getPubckey(e,n):
    n = int.from_bytes(n, byteorder='little')
    e = 65537

    # 使用(e, n)初始化RSAPublicNumbers，并通过public_key方法得到公钥
    # construct key with parameter (e, n)
    key = rsa.RSAPublicNumbers(e, n).public_key(default_backend())


@app.route('/getToken', methods=['POST'])
def generate_jwt():
    # retrieve user ID from X-ARR-ClientCert header
    client= request.headers.get('X-ARR-ClientCert')
    print(client)

    if client is None:
        return getCerErrorMessage("X-ARR-ClientCert is Empty"),400
    else:
        with app.app_context():
            Certificate = Callcertificate.query.filter_by(Certificate=client).first()
            if Certificate is None:
                return getCerErrorMessage("X-ARR-ClientCert is Wrong"),400
            else:
                jwt_payload = {'user_id': Certificate.id,'due_time':time.time()+1800}
                print(jwt_payload)
                jwt_token = jwt.encode(jwt_payload, secret_key, algorithm='HS256')
                publickey = Certificate.publickey
                print(publickey)
                

                token=rsa.encrypt(jwt_token.encode(),p)
                return {"accessToken":token,'accessExpiresIn':1800,'tokenType':"1"},200

def createToken():
    expires = datetime.timedelta(seconds=1800)
    token = create_access_token(identity='user_id', expires_delta=expires)
def checkToken(request):
    token = request.headers.get('Token')
    if token is None:
        return getCerErrorMessage("Token is Empty"),400
    else:
        try:
            jwt_payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        except jwt.exceptions.InvalidSignatureError:
            return getCerErrorMessage('Invalid JWT signature',401),
        if jwt_payload['exp'] < time.time():
            return getCerErrorMessage('JWT has expired', 401)
@app.route('/elevators/calls', methods=['POST'])
def elevatorsCalls():
    token = request.headers.get('Token')
    equimentNUmber = request.json['equipmentNumber']
    enterfloor=request.json['entry']['floorNumber']
    exitfloor =request.json['exit']['floorNumber']
    requestType=request.json['requestType']
    label=request.json['entry']['sideLabel']
    if token is None:
        return getCerErrorMessage("Token is Empty"),400
    else:
        try:
            jwt_payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        except jwt.exceptions.InvalidSignatureError:
            return getCerErrorMessage('Invalid JWT signature',401),
        if jwt_payload['exp'] < time.time():
            return getCerErrorMessage('JWT has expired', 401)
        user_id = jwt_payload['user_id']
         # check power
        with app.app_context():
            equimentExist=CallEquipmentNumber.query.filter_by(equipmentnuber=equimentNUmber).first()
            if equimentExist is None:
                getCerErrorMessage("equipmentnumber not exist",401)
            power=Callpower.query.filter_by(certificateid=user_id).first()
            if power is None:
                getCerErrorMessage("equipmentnumber Permission denied",401)
            if equimentExist.userId in None:
                equimentExist.userId=""
            # 检查 requestType
            # 检查 mqtt 是否连接
            groupId=equimentExist.userId
            connected=mqtt.mqtt_isconnect()
            mode=mqtt.elevatorMode[equimentNUmber]
            if mode is None:
                mode="EleUnv"
            if mode=="PTravelOp":
                if groupId=="":
                    #单任务模式，首先判断是否存在任务
                    task=elevatorTask[equimentNUmber]
                    if task is None:
                        pass
                    else:
                        getCallCallParam("Unavailable","","Current elevator has a task",request.json,groupId),200
                else:
                    mapGroup=CallEquipmentNumber.query.filter_by(userId=groupId).all()
                    grouplist=[]
                    for callEquipment in mapGroup:
                        print(callEquipment.equipmentnuber)
                        grouplist.append(callEquipment.equipmentnuber)
                    elevatorGroupMap[groupId]=grouplist
                # 进行判断评估还是真的
                if requestType=="Request":
                    callStatus='CallAccepted'
                    direction = "Down"
                    if enterfloor-exitfloor>0:
                        direction='Down'
                    else:
                        direction='up'
                # 产生uuid
                    my_uuid = uuid.uuid4()
                #进行外呼
                    mqtt.start_sending_floor_call(equimentNUmber,label,enterfloor,direction)
                #进行存储
                    calleleparams=Calleleparams(
                        callid=my_uuid,
                        maxweight='0',
                    enterfloornumber = request.json['entry']['floorNumber'],
                    enterfloor = '',
                    equipmentNumber = request.json['equipmentNumber'],
                    elevatorGroupId = groupId,
                    callStatus = callStatus,
                    requestType = request.json['requestType'],
                    exclusive = request.json['exclusive'],
                    callStatusReason = "",
                    exitfloornumber = request.json['exit']['floorNumber'],
                    entersidelabel = request.json['entry']['sideLabel'],
                    exitsidelabel = request.json['entry']['sideLabel'],
                    callerState = '',
                    isCancel = False,
                    FirstTemp = time.time(),
                    FinalTemp = time.time()

                    )
                    db.session.add(calleleparams)
                    db.session.commit()
                    elevatorTask[equimentNUmber]= {"callStatus":callStatus,"equimentNumber"
                :equimentNUmber,"FirstTemp":time.time(),"FinalTemp":time.time()}
                    return getCallCallParam(callStatus,my_uuid,'',request.json,groupId)


                else:
                    return getCallCallParam('Available',"",'',request.json,groupId),200


            else:
                return getCallCallParam("Unavailable","",mode,request.json,groupId),200



@app.route('/elevators/calls/<callId>', methods=['GET'])
def getElevatorsCalls(callId):
    checkToken(request)
    with app.app_context():
        calleleparams=Calleleparams.query.filter_by(callid=callId).first()
        if calleleparams is None:
            return getCerErrorMessage("callId is not find",400)
        else:
            callStatus=calleleparams.callStatus
            mqttpolicy = MqttCallPolicy()
            if calleleparams.elevatorGroupId=='':
                #单任务电梯
                if callStatus=="CallAccepted" or callStatus=='EnterAccepted':


                    status,equipmentNUmber=mqttpolicy.changeCallStutus(calleleparams,mqtt)

                    if status is None:
                        pass
                    else:
                        calleleparams.callStatus=status
                        calleleparams.equipmentNumber=equipmentNUmber
                        calleleparams.FirstTemp=time.time()
                        calleleparams.FinalTemp=time.time()
                        db.session.commit()
                        elevatorTask[calleleparams.equipmentNumber]= {"callStatus":callStatus,"equimentNumber"
                    :equipmentNUmber,"FirstTemp":time.time(),"enterFloorNum":calleleparams.enterfloornumber,"enterSide":calleleparams.entersidelabel
                            ,"FinalTemp":time.time(),'isCancel':False,"exitFloorNum":calleleparams.exitfloornumber,"exitSide":calleleparams.exitsidelabel}
            else:
                #群组电梯
                if callStatus=="CallAccepted" or callStatus=='EnterAccepted':
                    status,equipmentNUmber=mqttpolicy.ChangeGoupIdCallStatus(calleleparams,mqtt,elevatorGroupMap)
                    if status is None:
                        pass
                    else:
                        calleleparams.callStatus=status
                        calleleparams.equipmentNumber=equipmentNUmber
                        calleleparams.FirstTemp = time.time()
                        calleleparams.FinalTemp = time.time()
                        db.session.commit()
                        elevatorTask[calleleparams.equipmentNumber] = {"callStatus": callStatus, "equimentNumber"
                        : equipmentNUmber, "FirstTemp": time.time(), "enterFloorNum": calleleparams.enterfloornumber,
                                                                       "enterSide": calleleparams.entersidelabel
                            , "FinalTemp": time.time(), 'isCancel': False,
                                                                       "exitFloorNum": calleleparams.exitfloornumber,
                                                                       "exitSide": calleleparams.exitsidelabel}
            mode=mqtt.elevatorMode[equipmentNUmber]
            if mode is None:

                calleleparams.callStatus="Aborted"
                calleleparams.callStatusReason="mode is None"
                calleleparams.isCancel=True
                db.session.commit()
            else:
                if mode =="PTravelOp":
                    if calleleparams.callStatus=="CallAccepted":
                        calleleparams.callStatus="TravelToEntryFloor"
                    if calleleparams.callStatus=="EnterAccepted":
                        calleleparams.callStatus="TravelToExitFloor"
                    if calleleparams.callStatus=='ExitAccepted':
                        calleleparams.callStatus="Done"
                        #移除任务
                        elevatorTask.pop(equipmentNUmber)
                    if calleleparams.callStatus=='AbortAccepted':
                        calleleparams.callStatus='Aborted'
                        elevatorTask.pop(equipmentNUmber)
                    if calleleparams.callStatus=="Enter" or Calleleparams.callStatus=="Exit":
                        calleleparams.FinalTemp=time.time()

                        elevatorTask[calleleparams.equipmentNumber]['FinalTemp']=time.time()
                    db.session.commit()


                else:
                    calleleparams.callStatus = "Aborted"
                    calleleparams.callStatusReason = mode
                    calleleparams.isCancel = True
                    db.session.commit()
                return getCallParams(callparams=calleleparams),200


@app.route('/elevators/calls/<callId>',methods=['Patch'])
def updateElevatorCalls(callId,callerstate):
    checkToken(request)
    with app.app_context():
        calleleparams = Calleleparams.query.filter_by(callid=callId).first()
        if calleleparams is None:
            return getCerErrorMessage("callId is not find", 400)
        else:
            if calleleparams.callStatus=="Aborted" or calleleparams.callStatus=="AbortAccepted":
                calleleparams.callStatus="Aborted"
                calleleparams.callStatusReason="Wrong state transition, current state"
                return getCerErrorMessage("Wrong state transition, current state",400)
            else:
                if calleleparams.callStatus=="Enter" and callerstate=="Enter":
                    calleleparams.callerState="Enter"
                    calleleparams.callStatus="EnterAccepted"
                    calleleparams.isCancel=True
                    #进行内呼
                    mqtt.send_cabin_call(calleleparams.equipmentNumber,calleleparams.exitsidelabel,calleleparams.exitfloornumber)
                    db.session.commit()
                elif calleleparams.callStatus=="Exit" and callerstate=="Exit":
                    calleleparams.callerState = "Exit"
                    calleleparams.callStatus = "ExitAccepted"
                    calleleparams.isCancel = True
                    # 进行内呼
                    elevatorTask.pop(calleleparams.equipmentNumber)
                    db.session.commit()
                else:
                    getCerErrorMessage("Wrong state transition, current state",400)
                return getCallParams(calleleparams),200

@app.route('/elevators/calls/<callId>',methods=['delete'])
def deleteElevatorsCalls(callId):
    checkToken(request)
    with app.app_context():
        calleleparams = Calleleparams.query.filter_by(callid=callId).first()
        if calleleparams is None:
            return getCerErrorMessage("callId is not find",400)
        else:
            calleleparams.callStatus="AbortAccepted"
            calleleparams.isCancel=True
            db.session.commit()
            elevatorTask.pop(calleleparams.equipmentNumber)
            return getCallParams(calleleparams),200

@app.route('/elevators/<equipmentNumber>/floors',methods=['GET'])
def getEquipmentNumberFloors(equipmentNumber):
    checkToken(request)
    if equipmentNumber is None:
        return getCerErrorMessage("equipmentNumber is Empty",400)
    else:
        floors=mqtt.elevatorfloors[equipmentNumber]
        list=[]
        for floor in floors:
            floorside={"floorNumber":floor,'floorName':equipmentNumber,'floorLabel':'','floorType':'Parking',
                 'sideItems':[{'sideName':'','floorSide':'','sideType':'','sideRestriction':True}],'hiddenFloor':True}
            list.append(floorside)
        return list,200

@app.route('/elevators/{equipmentNumber}/drives',methods=['GET'])
def getEquipmentNumberdrives(equipmentNumber):
    checkToken(request)
    if equipmentNumber is None:
        return getCerErrorMessage("equipmentNumber is Empty", 400)
    else:
        direction=mqtt.elevatorDiraction[equipmentNumber]
        if direction is None:
            return getCerErrorMessage('equipmentNumber not exist',400)
        else:
            return {'driveHealthState':"Undefined",'nextTravelDirection':direction,'aes':{'battery':{'aesBatteryCharge':'NotReadable'}}},200

@app.route('/elevators/<equipmentNumber>/cabins',methods=['GET'])
def getEquipmentNumberCabins(equipmentNumber):
    checkToken(request)
    if equipmentNumber is None:
        return getCerErrorMessage("equipmentNumber is Empty", 400)
    else:
        position=mqtt.elevatorPosition[equipmentNumber]
        if position is None:
            return getCerErrorMessage('equipmentNumber not exist',400)
        else:
            return [{'deck':'','cabinPosition':position,'inDoorZone':'','passengerInCabin':'',"passengerTrapped":'',
                         'emergencyLightActive':'','carVentilationActive':''}],200

@app.route('/elevators/<equipmentNumber>/cabins/<deck>/door',methods=['POST'])
def deckDoor(equipmentNumber,deck):
    checkToken(request)
    if equipmentNumber is None:
        return getCerErrorMessage("equipmentNumber is Empty", 400)
    else:
        if deck=="Lower":
            return getCerErrorMessage("deck is wrong",400)
        door = mqtt.elevatorDoor[equipmentNumber]
        if door is None:
            return getCerErrorMessage('equipmentNumber not exist',400)
        else:
            list=[]
            doorside={'sideLabel':'','doorState':door,'doorHealthState':'OK'}
            list.append(doorside)
            return list,200





def  getCallParams(callparams):
    return {
            "callId": callparams.callid,
            'equipmentNumber': callparams.equipmentNumber,
            'entry': {'floorNumber':callparams.enterfloornumber,"sideLabel":callparams.entersidelabel},
            'exit': {'floorNumber':callparams.exitfloornumber,'sideLabel':callparams.exitsidelabel},
            'elevatorGroupId': callparams.elevatorGroupId,
            'callStatus': callparams.callStatus,
            'requestType': callparams.requestType,
            'exclusive': callparams.exclusive,
            'maxRobotWeight': callparams.maxweight,
            'callStatusReason': callparams.callStatusReason,
            'callerState': callparams.callerState
        }
def  getCallCallParam(callStatus,uuid,reason,requst,groupId):
    return {
            "callId":uuid,
            'equipmentNumber':requst.json['equipmentNumber'],
            'entry':requst['entry'],
            'exit':requst['exit'],
            'elevatorGroupId':groupId,
            'callStatus':callStatus,
            'requestType':requst.json['requestType'],
            'exclusive':requst.json['exclusive'],
            'maxRobotWeight':"0.0",
            'callStatusReason':reason,
            'callerState':""
        }

if __name__ == '__main__':
    server = pywsgi.WSGIServer(('127.0.0.1', 5000), app)
    server.serve_forever()








