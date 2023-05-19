import uuid
import datetime
import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask
Base = declarative_base()


class TDog(Base):
    __tablename__ = "dog"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String(256), nullable=True)
    uuid = sqlalchemy.Column(sqlalchemy.String(64), unique=True)
    addtime = sqlalchemy.Column(sqlalchemy.DateTime())
    data = sqlalchemy.Column(sqlalchemy.Text(), default='{}')

    def __init__(self, name, uuid, data='{}', addtime=None):
        self.name = name
        self.uuid = uuid
        self.data = data
        self.addtime = addtime if None != addtime else datetime.datetime.now()
app = Flask(__name__)
DIALECT = 'mysql'
DRIVER = 'mysqlconnector'
USERNAME = 'rds_mysql_001'
PASSWORD = 'Michael@2019#@!'
HOST = 'rm-uf6h753a4k76243n7qo.mysql.rds.aliyuncs.com'
PORT = '3306'
DATABASE = 'schindler'


SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT, DRIVER, USERNAME, PASSWORD, HOST, PORT,
                                                                       DATABASE)
url = 'postgresql://dbuser:dbpassword@127.0.0.1:5432/zoodb'
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
db = sqlalchemy(app)
engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URI)
metadata = sqlalchemy.schema.MetaData(bind=engine)
Base.metadata.create_all(engine)  # 创建表结构

Session = orm.sessionmaker(bind=engine)


def admq():
    sess = Session()

    # 增加一只狗
    uuidstr = str(uuid.uuid4())
    adog = TDog("doge", uuidstr)
    sess.add(adog)
    sess.commit()

    # 根据 uuid 字段，查询这只狗
    qdog = sess.query(TDog).filter(TDog.uuid == uuidstr).first()
    print("查询结果：", qdog.name, qdog.uuid, qdog.addtime)

    # 根据 uuid 字段修改这只狗
    data = {"name": "newdoge", "addtime": datetime.datetime.now()}
    sess.query(TDog).filter(TDog.uuid == uuidstr).update(data)
    sess.commit()
    # 查询一下修改后的结果
    qdog = sess.query(TDog).filter(TDog.uuid == uuidstr).first()
    print("修改后的查询结果：", qdog.name, qdog.uuid, qdog.addtime)

    # 根据 uuid 字段删除这只狗
    sess.query(TDog).filter(TDog.uuid == uuidstr).delete()
    sess.commit()
    # 查询一下修改后的结果
    qdog = sess.query(TDog).filter(TDog.uuid == uuidstr).first()
    if None == qdog:
        print("删除后：dog with uuid [{0}] is not exists".format(uuidstr))
    else:
        print("删除后：", qdog.name, qdog.uuid, qdog.addtime)


if "__main__" == __name__:
    admq()