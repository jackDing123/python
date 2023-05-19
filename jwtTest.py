import jwt
from flask_jwt_extended import create_access_token
import datetime
import time
import  rsa



def getToken():
    jwt_payload = {'user_id': 1, 'due_time': time.time() + 1800}
    print(jwt_payload)
    jwt_token = jwt.encode(jwt_payload, '1', algorithm='HS256')


    print(jwt_token)
    return jwt_token




token = getToken()
publickey='''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAjCJrlVw8RTOYSXL7f3+C
QItVOcnLYNQOTP5XRSJHwMyd3RWzj48ET1wLdyswev0jvnjcXgFU32DpnATDv4/m
d24bnPHBVDvmTlwafaUIjW4A6fht2xkDa8y7NHx1vEjnatOKUaYz6S6QwitEpfOK
jJSb1BJ4FX0Ar/c79XaLCxAkoNu+6uPENqOlb6eAtb1qhgecl9EgvPsPHQw0thH0
8r5xQuEDfHC2vGnj7d/slVLR3zweEuyJ31nDw54ZMXMW9sjg/RPEjBHoZvEL1sR4
7GxMAYgc77FKG22qo05mwNl/ibejNySdC6ebFdgseC5X4Zk+j4ceVlepMGjI8l07
4QIDAQAB
-----END PUBLIC KEY-----'''
ciphertext = public_key.encrypt(
    message,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

