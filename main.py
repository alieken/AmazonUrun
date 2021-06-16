from bs4 import BeautifulSoup
import requests
import sqlalchemy as db
import psycopg2


#sqlalchemy ile postgresqle bağlanıldığı kısım
engine = db.create_engine('(postgresqladresiniz)')
connection = engine.connect()
metadata = db.MetaData()
tablo = db.Table('kategoribilgileri', metadata, autoload=True, autoload_with=engine)
print("Tablo Bilgileri")
print(tablo.columns.keys())
print(repr(metadata.tables['kategoribilgileri']))

asinler=[]
isimler=[]

#sitelerden alınan bilgilere göre asin ve ürün başlıklarının düzenlenip dizilere kaydedildiği kısım
def getasinandnames(titlestr):
    global asinler
    global isimler
    splitler = titlestr.split('<div class="sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col sg-col-4-of-20" ')
    for i in range(1, len(splitler)):
        splitler2 = splitler[i].split('data-asin="')
        splitler3 = splitler2[1].split('"')
        asinler.append(splitler3[0])
        splitler4 = splitler[i].split('<img alt=')
        splitler5 = splitler4[1].split(' class')
        isimlerstr = splitler5[0]
        isimlerstr = isimlerstr.replace('\'', '')
        isimlerstr = isimlerstr.replace('"', '')
        isimler.append(isimlerstr)


#amazonda belirlediğim kategorinin 2 sayfasının xml kodlarının alındığı ve stringe çevrildiği kısım
HEADERS = ({'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36','Accept-Language': 'en-US, en;q=0.5'})

#sayfa1
page1 = "https://www.amazon.com.tr/s?i=computers&rh=n%3A12601898031%2Cp_72%3A13136589031&pf_rd_i=12601898031&pf_rd_p=cfb77c46-bf57-58e8-973b-35571c6737f8&pf_rd_r=SH8W7DG6MK8HE16FECV3&pf_rd_s=merchandised-search-10&pf_rd_t=BROWSE&qid=1621690146&ref=sr_pg_1"
r1=requests.get(page1,params=HEADERS)
source1 = BeautifulSoup(r1.content,"lxml")
title1 = source1.findAll("div",attrs={"class": 'sg-col-4-of-20'})
titlestr1=str(title1)
getasinandnames(titlestr1)

#sayfa2
page2="https://www.amazon.com.tr/s?i=computers&rh=n%3A12601898031%2Cp_72%3A13136589031&page=2&pf_rd_i=12601898031&pf_rd_p=cfb77c46-bf57-58e8-973b-35571c6737f8&pf_rd_r=SH8W7DG6MK8HE16FECV3&pf_rd_s=merchandised-search-10&pf_rd_t=BROWSE&qid=1621759692&ref=sr_pg_2"
r2=requests.get(page2,params=HEADERS)
source2 = BeautifulSoup(r2.content,"lxml")
title2 = source2.findAll("div",attrs={"class": 'sg-col-4-of-20'})
titlestr2=str(title2)
getasinandnames(titlestr2)


print("")
print("Web sitesinden alınan asin ve başlıklar")
for i in range(0,len(asinler)):
    print("asin : ", asinler[i], " isim : ", isimler[i])


#postgresql için veritabanına ekleme ve veritabanından çekilen rowların gösterildiği kısım
sayac=1
Values=[]
for i in range(0,len(asinler)):
    value={'id':sayac, 'asin':asinler[i], 'isim':isimler[i]}
    Values.append(value)
    sayac=sayac+1

#insert
query = db.insert(tablo)
ResultProxy = connection.execute(query,Values)


#select
selectquery= db.select([tablo])
ResultProxyselect = connection.execute(selectquery)
ResultSet = ResultProxyselect.fetchall()
print("")
print("Postgresql veritabanından gelen veriler")
for i in ResultSet:
    print(i)
