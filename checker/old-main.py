import requests
import sys
import time
import datetime
import csv
import os

print("-----")
print(os.path.dirname(__file__))
print("-----")

Domain = ""  # example.com
limit = 100
offset = 0
roop = 1

def WriteCsv():
    dt_now = datetime.datetime.now()
    with open(os.path.dirname(__file__) + '/' + Domain + "-" + dt_now.strftime('%Y%m%d-%H%M%S') + '.csv', 'x', newline="", encoding="utf-8_sig") as f:
        writer = csv.writer(f)
        writer.writerow(serverList)

serverList = []
for i in range(roop):

    notRespondingServers = requests.post("https://" + Domain + "/api/federation/instances", json={
        "host" : '',
        "blocked" : False,
        "notResponding" : False,
        "suspended" : False,
        "federating" : False,
        "subscribing" : False,
        "publishing" : False,
        "limit" : limit,
        "offset" : offset
    }, timeout=(9.0, 16.0))

    if 200 <= notRespondingServers.status_code <= 299:
        GetJsonData = notRespondingServers.json()
        if len(GetJsonData) == 0:
            WriteCsv()
            print("表示できるデータがこれ以上存在しません.")
            input(">> 終了するにはキーを押下してください.")
            sys.exit()
    else:
        print("ERROR: StatusCode: " + str(notRespondingServers.status_code))
        sys.exit()

    print(GetJsonData)

    for server in GetJsonData:
        
        try:
            pingCheck = requests.get("https://" + server["host"], timeout=(9.0, 16.0))
            print(server["host"] + " Status: " + str(pingCheck.status_code))
            if 200 <= pingCheck.status_code <= 299:
                pass
            elif 500 <= pingCheck.status_code <= 499:
                pass
            else:
                name = server["name"] if server["name"] != None else server["host"]
                softwareName = server["softwareName"] if server["softwareName"] != None else "Unknown"
                serverList.append({
                        "domain" : server["host"],
                        "name" : name,
                        "software" : str.lower(softwareName)
                })
        except:
            print(server["host"] + " Status: Not response.")
            name = server["name"] if server["name"] != None else server["host"]
            softwareName = server["softwareName"] if server["softwareName"] != None else "Unknown"
            serverList.append({
                    "domain" : server["host"],
                    "name" : name,
                    "software" : str.lower(softwareName)
            })

        #time.sleep(0.1)
    
    offset += limit
    print("---" + str(limit) + "---")
    time.sleep(1)

WriteCsv()

print("Offset: " + str(offset))
print(serverList)

input(">> 終了するにはキーを押下してください.")