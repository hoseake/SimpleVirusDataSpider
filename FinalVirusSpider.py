import requests
from bs4 import BeautifulSoup
import re
import pymysql
import json
response = requests.get('https://ncov.dxy.cn/ncovh5/view/pneumonia') #获取URL响应
homePage = response.content.decode()
soup = BeautifulSoup(homePage,'lxml') # 转化为soup对象
script = soup.find(id='getListByCountryTypeService2true') # 使用查找方法查找并取出对应id值的标签
text = script.text
json_str = re.findall(r'\[.+\]',text)[0] # 正则表的式进一步提取
lastDay_CoronaVirus = json.loads(json_str) # 将json字符串转化为python对象
# print(lastDay_CoronaVirus)
with open('lastDay_CoronaVirus.json','w',encoding='utf-8') as fp:
    json.dump(lastDay_CoronaVirus,fp,ensure_ascii=False) #将python对象转化为json并写入
"""连接一个数据库，并创建表"""
mysql_connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='183655', db='virus_db')
# 连接数据库,必须指定一个数据库,所以只能手动新建一个
cur = mysql_connection.cursor()  # 创建游标
sql_create = """
    CREATE TABLE virus_data (
地区 varchar(20) NOT NULL PRIMARY KEY,
确诊人数 int NOT NULL,
疑似人数 int NOT NULL,
治愈人数 int NOT NULL,
死亡人数 int NOT NULL);
"""
# 以上为创建数据库和表的sql语句
# # 异常捕获处理
a = open(r"lastDay_CoronaVirus.json", "r",encoding='UTF-8')
out = a.read() #参数为空，读取整个文件
# tmp = json.dumps(out) # 将python对象编码成Json字符串
tmp = json.loads(out) # 将Json字符串解码成python对象，必须要先转化才可以变成python可操作对象
num = len(tmp)
i = 0
try:
    cur.execute(sql_create) # 通过游标执行创建语句
    print("创建表成功")
except Exception as e: # 若try中语句发生异常的异常处理
    print(e)
    print("创建表失败或表已存在")
while i < num:
    pName = tmp[i]['provinceName']
    conCount = tmp[i]['confirmedCount']
    susCount = tmp[i]['suspectedCount']
    curCount = tmp[i]['curedCount']
    deaCount = tmp[i]['deadCount']
    #value = [pName,conCount,susCount,curCount,deaCount]
    sql_insert = "replace into virus_data (地区,确诊人数,疑似人数,治愈人数,死亡人数) values (\"%s\",\"%d\",\"%d\",\"%d\",\"%d\")"%(str(pName),int(conCount),int(susCount),int(curCount),int(deaCount))
    #因为在这里例如tmp[i]['provinceName']返回的是字符串：美国，所以values里每一个%s都要添加双引号，不然会抛出Unknown column '美国' in 'field list'的错误
    # sql_insert =("insert into daxue (code,charge,level,name,remark,prov) values (%s,%s,%s,%s,%s,%s);",value)
    # sql_insert = sql_insert.encode("utf8")
    #print(sql_insert)
    cur.execute(sql_insert)  # 执行上述sql命令
    i = i+1
print(num) # 打印更新行数
mysql_connection.commit()
cur.close()
mysql_connection.close()