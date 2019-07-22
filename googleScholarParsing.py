from bs4 import BeautifulSoup
import urllib.request
import pandas as pd
from datetime import datetime, timedelta


import smtplib, os  # smtplib: 메일 전송을 위한 패키지
from os.path import basename
from email import encoders  # 파일전송을 할 때 이미지나 문서 동영상 등의 파일을 문자열로 변환할 때 사용할 패키지
from email.mime.text import MIMEText   # 본문내용을 전송할 때 사용되는 모듈
from email.mime.multipart import MIMEMultipart   # 메시지를 보낼 때 메시지에 대한 모듈
from email.mime.application import MIMEApplication

dt = datetime.now()
now = dt.strftime('%Y-%m-%d %Hh%Mm%Ss')
now_date = dt.strftime('%Y-%m-%d')
location="c:/intel/google_"+now+".csv"

def parsing(now_date,location) :

    titles = []
    links = []
    dates = []
    pages = ['0', '10', '20', '30', '40', '50']
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    print('Crawing google scholar...')

    for pg in pages:
        url=urllib.request.Request('https://scholar.google.co.kr/scholar?start='+pg+'&q=aspirin&hl=ko&scisbd=1&as_sdt=0,5', headers=headers)
        page=urllib.request.urlopen(url).read()
        bs=BeautifulSoup(page,'html.parser')
        htmls=bs.find_all(class_='gs_rt')
        days=bs.find_all(class_='gs_age')
        if len(days)!=len(htmls):
            diff=len(htmls)-len(days)
            for i in range(diff):
                days.append(days[-1])

        for html in htmls:
            link=html.a['href']
            title=html.get_text()
            title = title.replace(",", "")
            title = title.strip('…')
            titles.append(title)
            links.append(link)

        for day in days:
            date = day.get_text()[0]
            before=int(date)
            before = 10
            theday = dt - timedelta(days=before)
            theday = theday.strftime("%Y-%m-%d")
            dates.append(theday)

    result={'Parse_Date':dates,'Doc_Title':titles,'Doc_Link':links}
    df=pd.DataFrame(result)
    df.to_csv(location,index="False", sep=',', encoding='utf-8')
    send_mail(result,location)
    return

def send_mail(result,location):

    print('Sending mail...')
    server=smtplib.SMTP('smtp.gmail.com',587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login('med.scholar.bot@gmail.com','gaongkwkebqbdthl')
    sent_from= 'med.scholar.bot'
    addrs =['idchuem@gmail.com','idchuem@naver.com']
    subject = "[Daily report] Med Scholar Bot_"+now_date
    text ='Please check the attachment.'

    body = MIMEText(text)
    msg=MIMEMultipart()
    msg['From']= sent_from
    msg['Subject'] = subject
    msg.attach(body)

    with open(location, "rb") as file:
        part = MIMEApplication(file.read(), Name=basename(location))
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(location)
        msg.attach(part)

    for to in addrs:
        msg['To'] = to
        server.sendmail(sent_from,to,msg.as_string())

    print('mail has sent')
    server.quit()

print('Excuting Program')
parsing(now_date,location)
print('Finished')
