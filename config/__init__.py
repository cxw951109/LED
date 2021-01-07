import datetime
import time
from sqlalchemy import Column, String,Integer,create_engine,ForeignKey
from sqlalchemy.orm import sessionmaker,relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

engine = create_engine("mysql+pymysql://root:111@127.0.0.1/test5")

Base = declarative_base()

# def func1(start,end, date_list=[]):
#     target = (start + datetime.timedelta(days=1))
#     target_res = target.strftime("%Y-%m-%d")
#     date_list.append(target_res)
#     if target == end:
#         pass
#     else:
#         func1(target,end,date_list)
#     return date_list

def func(today, date_list=[], count=0):
    target = (today - datetime.timedelta(days=1))
    target_res = today.strftime("%Y-%m-%d")
    date_list.append(target_res)
    count += 1
    if count >= 7:
        pass
    else:
        func(target, date_list, count)
    return date_list

#折线图
def chart1(value):
    data = []
    data1 = []
    data2 = []
    data3 = []
    today = datetime.date.today()
    today_res = today.strftime("%Y")
    target = (today - datetime.timedelta(days=8))
    target_res = target.strftime("%Y-%m-%d")
    date_list = func(today, [])
    m_list =['01','02','03','04','05','06','07','08','09',10,11,12]
    if value !='':
        query = session.query(Dailydata).filter(Dailydata.created_time.between(target_res, today),Dailydata.standard_name.like("%" + value + "%")).all()
        query1 = session.query(Dailydata).filter(Dailydata.created_time.contains(today_res),Dailydata.standard_name.like("%" + value + "%")).all()
    else:
        query = session.query(Dailydata).filter(Dailydata.created_time.between(target_res, today)).all()
        query1 = session.query(Dailydata).filter(Dailydata.created_time.contains(today_res)).all()
    for i in date_list:
        data.append(sum([x.goodNum for x in query if x.created_time == i]))
        data1.append(sum([x.badNum for x in query if x.created_time == i]))
    for n in m_list:
        data2.append(sum([x.goodNum for x in query1 if x.created_time.split('-')[1] ==str(n)]))
        data3.append(sum([x.badNum for x in query1 if x.created_time.split('-')[1] ==str(n)]))
    series = [
        {
            "name": '合格',
            "data": data,
            "type": 'line'
        },
        {
            "name": '劣质',
            "data": data1,
            "type": 'line'
        }
    ]
    series1 = [
        {
            "name": '合格',
            "data": data2,
            "type": 'line'
        },
        {
            "name": '劣质',
            "data": data3,
            "type": 'line'
        }
    ]
    return [series,date_list,series1]

#饼图
def chart2(value,start,end):
    if start !='':
        start =start.strftime("%Y-%m-%d")
        end =end.strftime("%Y-%m-%d")
        if value !='':
            query = session.query(Dailydata).filter(Dailydata.standard_name.like("%" + value + "%"),Dailydata.created_time.between(start, end)).all()
            query1 =session.query(Baddata).filter(Baddata.standard_name.like("%" + value + "%"),Baddata.created_time.between(start, end)).all()
        else:
            query = session.query(Dailydata).filter(Dailydata.created_time.between(start, end)).all()
            query1 =session.query(Baddata).filter(Baddata.created_time.between(start, end)).all()
    else:
        if value !='':
            query = session.query(Dailydata).filter(Dailydata.standard_name.like("%" + value + "%")).all()
            query1 =session.query(Baddata).filter(Baddata.standard_name.like("%" + value + "%")).all()
        else:
            query = session.query(Dailydata).all()
            query1 =session.query(Baddata).all()
    good =sum([x.goodNum for x in query])
    bad =sum([x.badNum for x in query])
    all =good+bad
    names =[1,2,3]
    series2 = []
    for i in names:
        series2.append({"value":sum([x.Num for x in query1 if x.types == i]),"name":i})
    if all !=0:
        all_pass_rate = '%.2f' % (good * 100 / (good+bad))
    else:
        all_pass_rate = '%.2f' % 0
    series3 =[
        {"value": good, "name": '合格'},
        {"value": bad, "name": '劣质'}
    ]
    series4=[all_pass_rate]
    return [series2,series3,series4]

#今日数据
def get_today():
    today = datetime.date.today()
    target_res = today.strftime("%Y-%m-%d")
    query = session.query(Dailydata).filter(Dailydata.created_time==target_res).first()
    if query:
        all =query.goodNum+query.badNum
        return all,query.goodNum,query.badNum
    else:
        return 0,0,0


class Dailydata(Base):
    __tablename__ = 'daily_data'

    id = Column(Integer(), primary_key=True,autoincrement=True)
    standard_name = Column(String(20))
    goodNum = Column(Integer)
    badNum = Column(Integer)
    created_time = Column(String(20))


class Baddata(Base):
    __tablename__ = 'bad_data'

    id = Column(Integer(), primary_key=True,autoincrement=True)
    Num = Column(Integer)
    standard_name = Column(String(20))
    types =Column(Integer)
    created_time = Column(String(20))


class Alert(Base):
    __tablename__ = 'alert'

    id = Column(Integer(), primary_key=True,autoincrement=True)
    mes =Column(String(100))
    created_time = Column(String(20))


class History(Base):
    __tablename__ = 'history'

    id = Column(Integer(), primary_key=True,autoincrement=True)
    url1 = Column(String(100))
    types =Column(Integer)
    standard_name = Column(String(20))
    created_time = Column(String(20))


    def __init__(self, url1, types,standard_name,created_time):
        self.types = types
        self.standard_name = standard_name
        self.url1 = url1
        self.created_time = created_time

    def to_dict(self):
        return {
            "id":self.id,
            "standard_name": self.standard_name,
            "types": self.types,
            "url1":self.url1,
            "created_time": self.created_time,
        }


class Standard(Base):
    __tablename__ = 'standard'

    id = Column(Integer(), primary_key=True,autoincrement=True)
    name = Column(String(20))
    rows =Column(String(10))
    columns = Column(String(10))
    wide =Column(String(10))
    high = Column(String(10))
    remarks =Column(String(50),default='')
    url1 = Column(String(100))
    url2 = Column(String(100))
    url3 = Column(String(100))
    url4 = Column(String(100))
    flag = Column(Integer,default=0)
    created_time = Column(String(20))

    def __init__(self, name, rows,columns,wide,high,remarks,url1,url2,url3,url4,created_time,flag):
        self.name = name
        self.rows = rows
        self.columns = columns
        self.wide = wide
        self.high = high
        self.remarks = remarks
        self.url1 = url1
        self.url2 = url2
        self.url3 = url3
        self.url4 = url4
        self.created_time = created_time
        self.flag = flag

    def to_dict(self):
        return {
            "id":self.id,
            "name": self.name,
            "rows": self.rows,
            "columns": self.columns,
            "wide": self.wide,
            "high": self.high,
            "remarks": self.remarks,
            "url1":self.url1,
            "url2": self.url2,
            "url3": self.url3,
            "url4": self.url4,
            "created_time": self.created_time,
            "flag": self.flag
        }


class Item(BaseModel):
    msg: str


class Item1(BaseModel):
    signal: list


class Item2(BaseModel):
    total: int
    standard_name: str
    result: list =[]


Base.metadata.create_all(engine)
MySession = sessionmaker(bind=engine)
session = MySession()