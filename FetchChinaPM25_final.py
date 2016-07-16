import datetime
import smtplib
import os
import time
import codecs
from bs4 import BeautifulSoup
import urllib2

def sendReport(foldersize):
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.ehlo()
    session.starttls()
    session.login("NOTSHOWN","NOTSHOWN")

    headers = "\r\n".join(["from:" + "ShuShi",
                           "subject:" + "RPi working fine",
                           "to:" + "shushi20002003@gmail.com",
                           "mime-version: 1.0",
                           "content-type: text/html"])
    content = headers + "\r\n\r\n" + "RPI is working fine ...\r\n\r\n, Folder size is %s kb" %str(foldersize)
    session.sendmail("Test", "shushi20002003@gmail.com", content)

def sendAlert():
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.ehlo()
    session.starttls()
    session.login("cguitar11@gmail.com","segovianoguitar")

    headers = "\r\n".join(["from:" + "ShuShi",
                           "subject:" + "RPi working fine",
                           "to:" + "shushi20002003@gmail.com",
                           "mime-version: 1.0",
                           "content-type: text/html"])
    content = headers + "\r\n\r\n" + "RPI needs some attention!"
    session.sendmail("Test", "shushi20002003@gmail.com", content)

def pro_city(input):
    city_name = input.text
    print city_name,

    if len(city_name)== 7:
        city_name = 'WuHai'

    if len(city_name)>1:
        city_url = "http://www.cnpm25.com"+input["href"]

    try:
        city_response = urllib2.urlopen(city_url)
        city_soup = BeautifulSoup(city_response.read().decode("utf-8"))
        city_time = city_soup.find("div",{"class":"rt-share"})

    except urllib2.HTTPError,err:
        print 'Found an HTTP error! Will try again in 30 seconds.'
        time.sleep(30)
        city_response = urllib2.urlopen(city_url)
        city_soup = BeautifulSoup(city_response.read().decode("utf-8"))
        city_time = city_soup.find("div",{"class":"rt-share"})
        #city_name = ''
        #city_time = ''
        #city_soup = ''
    except urllib2.URLError, err:
        print 'Found an URL error!Will try again in 30 seconds.'
        time.sleep(30)
        city_response = urllib2.urlopen(city_url)
        city_soup = BeautifulSoup(city_response.read().decode("utf-8"))
        city_time = city_soup.find("div",{"class":"rt-share"})
        #city_name = ''
        #city_time = ''
        #city_soup = ''

    return (city_name, city_time, city_soup)

#define a function to process each city
def writedatafile(inputname, inputtime, inputsoup):
    print 'printing files'
    strComma = u'\u002C'
    filename = inputname + ".csv"
    table = inputsoup.find("table")
    f = codecs.open(filename, "a+b", "utf-8")

    # get the time into format
    y = inputtime.text
    t = '/'.join([y[0:4], y[5:7],y[8:10] ]) + ' ' + y[12:14] + ':00'

    for row in table.findAll("tr"):
        global site
        global item
        site = row.findAll("td")
        #print t

        if site:
            f.write(t + strComma)
            f.write(site[0].text+ strComma)
            f.write(site[1].text.replace('\r', '').replace('\n','') + strComma)
            f.write(site[3].text.replace('\r', '').replace('\n','') + strComma)
            f.write(site[4].text.replace('\r', '').replace('\n','') +
strComma + u'\n')
    f.close()


# Main code
url = 'http://cnpm25.com'
r = urllib2.urlopen(url)
s = BeautifulSoup(r.read())
links = s.find_all("div",attrs={"class":"warp"})

time_dic = dict() # difine a empty dictionary to store time for each city

for x in links:
    link = x.findAll("a")
    for i in range(1,len(link)):
        city_name, city_time, city_soup = pro_city(link[i])
        writedatafile(city_name, city_time, city_soup)
        time_dic.update({city_name:city_time.get_text()})
        print city_name

count = 1
while count >0:
    print (time.strftime("%H:%M:%S"))
    print "Scanning the web..."
    for x in links:
        link = x.findAll("a")
        for i in range(1,len(link)):
            city_name, city_time, city_soup = pro_city(link[i])
            if city_name != '':
                if city_time.get_text() != time_dic[city_name]:
                    print "Found new time, updating files"
                    writedatafile(city_name, city_time, city_soup)
                    time.sleep(2)
                    time_dic.update({city_name:city_time.get_text()})
                else:
                    print "No new data"

    print (time.strftime("%H:%M:%S"))
    print "Idling..."

    # check status
    folder = '/media/2205-B870/PM25'
    foldersize = os.path.getsize(folder)
    t = time.strftime("%H")
    if (foldersize <= 2.5*100000000) &(t == "02"):
        sendReport(foldersize)
    elif foldersize > 2.5*100000000:
        sendAlert()
    else:
        pass
    time.sleep(60*5)
    count = count +1