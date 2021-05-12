import requests
from datetime import date
import sys
import smtpserver
import DBConfig
import psycopg2

from apscheduler.schedulers.blocking import BlockingScheduler


sched=BlockingScheduler()

#@sched.scheduled_job("interval",minutes=1)
def cron_job():
    today=date.today()
    todayString=today.strftime("%d-%m-20%y")
    params = DBConfig.config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    query="select * from public.userpage_userdetails"
    cur.execute(query)

    usersData=[]
    
    for row in cur.fetchall():
        temp_user={
            "mail":row[2],
            "pin":row[3],
            "district":row[4],
            "state":row[5]
        }
        usersData.append(temp_user)
    print("#####USER DATA######",usersData)
    for user in usersData:
        centre_names=[]
        if len(user['pin'])>0:
            url="https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode="+user["pin"]+"&date="+todayString 
        else:
            url="https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id="+user["district"]+"&date="+todayString
        print(url)
        response = requests.get(url, headers={
            "accept": "application/json",
            "Accept-Language": "hi_IN",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
        })
        if response.status_code != 200:
            print("Invalid response")
            continue
        print(response.json())
        centres=[]
        try:
            centres=response.json()['centers']
        except KeyError:
            print("No such ")
        
        if len(centres)==0:
            print("nothing to notify..no slots available")
        else:
            for centre in centres:
                sessions=centre['sessions']
                for session in sessions:
                    if session['available_capacity']>0:
                        centre_names.append(centre['name'])
        Content=""
        count=0
        for centre_name in centre_names:
            count=count+1
            Content= Content.__add__(str(count)+": "+ centre_name+"\n")
        #smtpserver.sendMail(user["mail"],Content)
        if Content:
            print("Sending mail to ====>",user["mail"])

            smtpserver.sendMail(user["mail"],Content)
        else:
            print("No slots available in any centres...")

    

cron_job()
sched.add_job(cron_job, 'interval', minutes=30)
sched.start()