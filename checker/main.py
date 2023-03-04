import requests
import sys
import time
import datetime
import os
from concurrent.futures import ThreadPoolExecutor

'''
print("-----")
print(os.path.dirname(__file__))
print("-----")
'''

Domain = ""  # example.com
limit = 100 # MAX:100
offset = 0
roop = 10

def WriteCsv():
    dt_now = datetime.datetime.now()
    with open(os.path.dirname(__file__) + '/' + Domain + "-" + dt_now.strftime('%Y%m%d-%H%M%S') + '.csv', 'x', newline="", encoding="utf-8_sig") as f:
        f.write("\n".join(serverList))
        #writer = csv.writer(f)
        #writer.writerow(serverList)

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

    # New
    def PingCheck(Domain, Name, SoftwareName):
        try:
            response = requests.get("https://" + Domain + "/.well-known/nodeinfo", timeout=(9.0, 16.0))
            print(Domain + " Status: " + str(response.status_code))
            if 200 <= response.status_code <= 299:
                return {
                    "host" : Domain,
                    "name" : Name,
                    "softwareName" : SoftwareName,
                    "reason" : str(response.status_code),
                    "isClosed" : False
                }
            elif 500 <= response.status_code <= 515:
                return {
                    "host" : Domain,
                    "name" : Name,
                    "softwareName" : SoftwareName,
                    "reason" : str(response.status_code),
                    "isClosed" : False
                }
            else:
                return {
                    "host" : Domain,
                    "name" : Name,
                    "softwareName" : SoftwareName,
                    "reason" : str(response.status_code),
                    "isClosed" : True
                }
        except:
            return {
                "host" : Domain,
                "name" : Name,
                "softwareName" : SoftwareName,
                "reason" : "Not response.",
                "isClosed" : True
            }

    futures = []
    serverList = []
    with ThreadPoolExecutor(max_workers=64, thread_name_prefix="thread") as pool:
        for server in GetJsonData:
            future = pool.submit(PingCheck, server["host"], server["name"], server["softwareName"])
            futures.append(future)
    for future in futures:
        ClosedCheck = future.result()
        if (ClosedCheck["isClosed"] == True):
            name = ClosedCheck["name"].replace("\"", "\\\"") if ClosedCheck["name"] != None else ClosedCheck["host"]
            softwareName = ClosedCheck["softwareName"].replace("\"", "\\\"") if ClosedCheck["softwareName"] != None else "Unknown"
            serverList.append("{"
                    + "\"domain\" : \"" + ClosedCheck["host"] + "\","
                    + "\"name\" : \"" + name + "\","
                    + "\"software\" : \"" + str.lower(softwareName) + "\","
                    + "\"reason\" : \"Other(" + ClosedCheck["reason"] + ")\""
            + "}")
    #
    '''
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
    '''
    offset += limit
    print("---" + str(limit) + "/" + str(offset) + "---")
    time.sleep(10)

WriteCsv()

print(serverList)
print("\n\nOffset: " + str(offset))

input(">> 終了するにはキーを押下してください.")