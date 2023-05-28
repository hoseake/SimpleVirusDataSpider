import requests
from bs4 import BeautifulSoup
import re
import pymysql
import json
import csv
import matplotlib.pyplot as plt
response = requests.get('https://ncov.dxy.cn/ncovh5/view/pneumonia')  # 获取URL响应
homePage = response.content.decode()
soup = BeautifulSoup(homePage, 'lxml')  # 转化为soup对象
script = soup.find(id='getListByCountryTypeService2true')  # 使用查找方法查找并取出对应id值的标签
text = script.text
json_str = re.findall(r'\[.+\]', text)[0]  # 正则表达式进一步提取
# print(json_str)
lastDay_CoronaVirus = json.loads(json_str)  # 将json字符串转化为python对象
# print(lastDay_CoronaVirus)
with open('CoronaVirusData.json', 'w', encoding='utf-8') as fp:
    json.dump(lastDay_CoronaVirus, fp, ensure_ascii=False)  # 将python对象转化为json并写入
"""连接一个数据库，并创建表"""
mysql_connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='183655', db='virus_db')
# 连接数据库,必须指定一个数据库,所以只能手动新建一个
# 运行时数据库要在后天打开，不然连接不了
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
a = open(r"CoronaVirusData.json", "r", encoding='UTF-8')
out = a.read()  # 参数为空，读取整个文件
# tmp = json.dumps(out) # 将python对象编码成Json字符串
tmp = json.loads(out)  # 将Json字符串解码成python对象，必须要先转化才可以变成python可操作对象
num = len(tmp)
i = 0
dictData = {}  # 为选择的国家疫情数据可视化创建字典
try:
    cur.execute(sql_create)  # 通过游标执行创建语句
    print("创建表成功")
except Exception as e:  # 若try中语句发生异常的异常处理
    print(e)
    print("创建表失败或表已存在")
while i < num:
    pName = tmp[i]['provinceName']  # 为存入数据库创建变量
    dictData[pName] = {}  # 在原有字典基础上创房二维字典
    dictData[pName]['countryName'] = pName
    conCount = tmp[i]['confirmedCount']
    dictData[pName]['conCount'] = conCount
    susCount = tmp[i]['suspectedCount']
    dictData[pName]['susCount'] = susCount
    curCount = tmp[i]['curedCount']
    dictData[pName]['curCount'] = curCount
    deaCount = tmp[i]['deadCount']
    dictData[pName]['deadCount'] = deaCount
    # value = [pName,conCount,susCount,curCount,deaCount]
    sql_insert = "replace into virus_data (地区,确诊人数,疑似人数,治愈人数,死亡人数) values (\"%s\",\"%d\",\"%d\",\"%d\",\"%d\")" % (
    str(pName), int(conCount), int(susCount), int(curCount), int(deaCount))
    # 因为在这里例如tmp[i]['provinceName']返回的是字符串：美国，所以values里每一个%s都要添加双引号，不然会抛出Unknown column '美国' in 'field list'的错误
    # sql_insert =("insert into daxue (code,charge,level,name,remark,prov) values (%s,%s,%s,%s,%s,%s);",value)
    # sql_insert = sql_insert.encode("utf8")
    # print(sql_insert)
    cur.execute(sql_insert)  # 执行上述sql命令
    i = i + 1
print(num)  # 打印更新行数
mysql_connection.commit()
cur.close()
mysql_connection.close()
# print(dictData)
while 1:  # 循环输入国家名称
    try:
        countryName = input("输入要查看数据的国家名称：")
        print(dictData[countryName])
    except Exception as e:  # 若try中语句发生异常的异常处理
        print("不存在此国家")
    dictDataConCount = dictData[countryName]['conCount']
    dictDataSusCount = dictData[countryName]['susCount']
    dictDataCurCount = dictData[countryName]['curCount']
    dictDataDeadCount = dictData[countryName]['deadCount']
    dictDataCountryName = dictData[countryName]['countryName']
    # 用来正常显示中文标签
    plt.rcParams['font.sans-serif'] = ['SimHei']
    labels = ['确诊病例', '疑似病例', '治愈病例', '死亡病例']  # 图标描述
    values = [dictDataConCount, dictDataSusCount, dictDataCurCount, dictDataDeadCount]  # 对应变量
    # print(values)
    # plt.ylim(0,100000000) #手动设置y轴上下限，不设置则按数据自动调整
    plt.title(dictDataCountryName + "疫情数据", fontsize=12, pad=15)  # 图表题目
    plt.tick_params(axis='both', which='major', labelsize=10)  # 图表各项属性
    plt.xlabel('病例分类')  # x轴标签
    plt.ylabel('病例人数')  # y轴标签
    plt.bar(labels, values, width=0.5, bottom=1, color="SkyBlue")
    # 在柱状图上显示具体数值，ha参数控制水平对齐方式，va控制垂直对齐方式
    for x, y in enumerate(values):  # 索引序列
        plt.text(x, y + 1, '%s' % y, ha='center', va='bottom', color='blue')
    plt.show()  # 显示图片
