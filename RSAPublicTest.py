
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import base64
import jwt
import rsa
from flask_jwt_extended import create_access_token
import datetime
import time
import json
import re
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
def pop_publickey(n,e):
    rase =65537
    rasm=int(n,16)
    key=rsa.RSAPublicNumbers(rase,rasm).public_key(default_backend())
    pem = key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    print(pem.decode())
    print(pem.decode().split('-----')[2])
    encryption(pem.decode(),"1")

    return  pem.decode()
def encryption(text: str, public_key: bytes):
	# 字符串指定编码（转为bytes）
	text = text.encode('utf-8')
	# 构建公钥对象
	cipher_public = PKCS1_v1_5.new(RSA.importKey(public_key))
	# 加密（bytes）
	text_encrypted = cipher_public.encrypt(text)
	# base64编码，并转为字符串
	text_encrypted_base64 = base64.b64encode(text_encrypted ).decode()
	return text_encrypted_base64

def encrypt(public_key, plaintext):
    key= public_key
    n=128
    # 对明文中的每个字符进行加密，并将结果存储在列表cipher中
    cipher = [(ord(char) ** key) % n for char in plaintext]
    return cipher


def getToken():
    jwt_payload = {'user_id': 1, 'due_time': time.time() + 1800}
    print(jwt_payload)
    jwt_token = jwt.encode(jwt_payload, '1', algorithm='HS256')


    print(jwt_token)
    return jwt_token


# 公钥加密
def rsadecrypt(pubkey, msg):
    """
    公钥加密
    :param pubkey: 公钥
    :param msg: 需要加密的字符串
    :return: 加密后的字符串
    """
    msg = json.dumps({"data": msg})

    data = ''
    msglen = len(msg)
    # 最大加密长度为：密钥长度/8-11  例如：1024/8-11=117
    list = cut_text(msg, 117)  # 切片
    for item in list:
        crypto = rsa.encrypt(item.encode(), pubkey)
        crypto = base64.b64encode(crypto).decode()
        data = data + crypto + " "
    data = data[0:len(data) - 1]
    return data


def cut_text(text, lenth):
    textArr = re.findall('.{' + str(lenth) + '}', text)
    textArr.append(text[(len(textArr) * lenth):])
    return textArr


def encrypt_data(msg,data):
    public_key = populate_public_key(data=data)  # 读取公钥信息
    cipher = PKCS1_cipher.new(public_key)  # 生成一个加密的类
    encrypt_text = base64.b64encode(cipher.encrypt(msg.encode()))  # 对数据进行加密
    print(encrypt_text)
    return encrypt_text.decode()  # 对文本进行解码码


def populate_public_key(data):
    # convert bytes to integer with int.from_bytes
    # 指定从little格式将bytes转换为int，一句话就得到了公钥模数，省了多少事
    n = int.from_bytes(data, byteorder='little')
    e = 65537

    # 使用(e, n)初始化RSAPublicNumbers，并通过public_key方法得到公钥
    # construct key with parameter (e, n)
    key = rsa.RSAPublicNumbers(e, n).public_key(128)
    pem = key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    print(pem.decode())

    return key
str='8C226B955C3C4533984972FB7F7F82408B5539C9CB60D40E4CFE57452247C0CC9DDD15B38F8F044F5C0B772B307AFD23BE78DC5E0154DF60E99C04C3BF8FE6776E1B9CF1C1543BE64E5C1A7DA5088D6E00E9F86DDB19036BCCBB347C75BC48E76AD38A51A633E92E90C22B44A5F38A8C949BD41278157D00AFF73BF5768B0B1024A0DBBEEAE3C436A3A56FA780B5BD6A86079C97D120BCFB0F1D0C34B611F4F2BE7142E1037C70B6BC69E3EDDFEC9552D1DF3C1E12EC89DF59C3C39E19317316F6C8E0FD13C48C11E866F10BD6C478EC6C4C01881CEFB14A1B6DAAA34E66C0D97F89B7A337249D0BA79B15D82C782E57E1993E8F871E5657A93068C8F25D3BE1'
publickey = pop_publickey(str, "65537")
token = getToken()

rsa.RSAPublicKey.encrypt(publickey,token)




