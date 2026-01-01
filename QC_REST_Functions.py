'''
Created by: Shilo Levavi 10/07/2023
REST api functions to GET data on bugs and releases from the QC ALM
contains the following functions:
- 


'''
import json
import requests
from requests.auth import HTTPBasicAuth

almUserName = "shilo"
almPassword = "sl171989"

almURL = "http://lotus:8080/qcbin/"
authEndPoint = almURL + "authentication-point/authenticate"
qcSessionEndPoint = almURL + "rest/site-session"
#IsConnected = almURL + "v2/rest/is-authenticated"
#GetEntity_defects = almURL + "rest/domains/PACKETLIGHT/projects/Main/customization/entities/defect/fields"
#GetEntity_defects = almURL + "rest/domains/PACKETLIGHT/projects/Main/customization/entities/defect"
#GetEntity_release = almURL + "rest/domains/PACKETLIGHT/projects/Main/customization/entities/release/"
GetRelease = almURL + "rest/domains/PACKETLIGHT/projects/Main/releases/1017" # get data for some release we created in QC under Management-> Releases. the number is the ID of that release in QC


cookies = dict()

headers = {
    'cache-control': "no-cache",
    'Accept': "application/json",
    'Content-Type': "application/json"
    }

   
def get_Release_QC(URL = almURL, username= almUserName, password = almPassword, domain = 'PACKETLIGHT',project = 'Main', release_id =None ):


    authEndPoint = URL + "authentication-point/authenticate"
    #print(authEndPoint)
    try:
        #response = self.Session.get(url = URL, auth=(username, password), verify = False, timeout=4)
        response = requests.post(url = authEndPoint, auth=(username, password), headers=headers)
        if response.status_code == 200:
            cookieName = response.headers.get('Set-Cookie')
            LWSSO_COOKIE_KEY = cookieName[cookieName.index("LWSSO_COOKIE_KEY=") + 17: cookieName.index(";")]
            cookies['LWSSO_COOKIE_KEY'] = LWSSO_COOKIE_KEY
            print('Logged in successfully')
        else:
            print(f"Can't login to QC server and the status code is {response.status_code}")

    except Exception as e:
        print(f"Exception is: {e}")

    qcSessionEndPoint = almURL + "rest/site-session"
    response = requests.post(qcSessionEndPoint, headers=headers, cookies=cookies)
    if response.status_code == 200 | response.status_code == 201:
        setCookies = response.headers.get('Set-Cookie').split(",")
        for setCookie in setCookies:
            cookieName = setCookie[0: setCookie.index("=")].strip()
            cookieValue = setCookie[setCookie.index("=") + 1: setCookie.index(";")]
            cookies[cookieName] = cookieValue
            if cookieName == 'XSRF-TOKEN':
                headers['X-XSRF-TOKEN'] = cookieValue

    else:
            print(f"Status code is {response.status_code}")



    releaseEndPoint = almURL +  f"rest/domains/{domain}/projects/{project}/releases/{str(release_id)}"
    #print(URL)
    Release_response = requests.get(releaseEndPoint, auth=(username, password), headers=headers, cookies=cookies)
    #print(Release_response)
    response_json = Release_response.json() # retrieve the release json values directly as dict
    #print(response_json)

    Rel_name = response_json['Fields'][4]['values'][0]['value'] # Release name like mentioned in the QC
    #print(Rel_name)
    Start_date = response_json['Fields'][7]['values'][0]['value'] # start date as 2023-07-09 format
    #print(Start_date)
    End_date = response_json['Fields'][0]['values'][0]['value'] # end date as 2023-07-09 format
    #print(End_date)
    return Rel_name, Start_date, End_date


def get_Test_QC(URL = almURL, username= almUserName, password = almPassword, domain = 'PACKETLIGHT',project = 'Main', release_id =None ):


    authEndPoint = URL + "authentication-point/authenticate"
    #print(authEndPoint)
    try:
        #response = self.Session.get(url = URL, auth=(username, password), verify = False, timeout=4)
        response = requests.post(url = authEndPoint, auth=(username, password), headers=headers)
        if response.status_code == 200:
            cookieName = response.headers.get('Set-Cookie')
            LWSSO_COOKIE_KEY = cookieName[cookieName.index("LWSSO_COOKIE_KEY=") + 17: cookieName.index(";")]
            cookies['LWSSO_COOKIE_KEY'] = LWSSO_COOKIE_KEY
            print('Logged in successfully')
        else:
            print(f"Can't login to QC server and the status code is {response.status_code}")

    except Exception as e:
        print(f"Exception is: {e}")

    qcSessionEndPoint = almURL + "rest/site-session"
    response = requests.post(qcSessionEndPoint, headers=headers, cookies=cookies)
    if response.status_code == 200 | response.status_code == 201:
        setCookies = response.headers.get('Set-Cookie').split(",")
        for setCookie in setCookies:
            cookieName = setCookie[0: setCookie.index("=")].strip()
            cookieValue = setCookie[setCookie.index("=") + 1: setCookie.index(";")]
            cookies[cookieName] = cookieValue
            if cookieName == 'XSRF-TOKEN':
                headers['X-XSRF-TOKEN'] = cookieValue

    else:
            print(f"Status code is {response.status_code}")


    # testsEndPoint = almURL +  f"rest/domains/{domain}/projects/{project}/tests/25249"
    testsEndPoint = almURL +  f"rest/domains/{domain}/projects/{project}/tests/13141"
    #testsEndPoint = almURL +  f"rest/domains/{domain}/projects/{project}/tests/7310"
    #testsEndPoint = almURL +  f"rest/domains/{domain}/projects/{project}/customization/entities/test"
    #testsEndPoint = almURL +  f"rest/domains/{domain}/projects/{project}/tasks/5/audits"
    #print(URL)
    Test_response = requests.get(testsEndPoint, auth=(username, password), headers=headers, cookies=cookies)
    print(Test_response)
    response_json = Test_response.json() # retrieve the release json values directly as dict
    print(response_json)

#ignore this
#a = get_Release_QC(URL = almURL, username= almUserName, password = almPassword, domain = 'PACKETLIGHT',project = 'Main', release_id = 1017 )
#print(a)

#a = get_Test_QC(URL = almURL, username= almUserName, password = almPassword, domain = 'PACKETLIGHT',project = 'Main', release_id = 1017 )
#print(a)

'''
createDomainUrl = almURL + "v2/sa/api/domains"
domainData = {'domain': {'name': 'PACKETLIGHT'}}
print(headers)
print(cookies)
response = requests.post(createDomainUrl, headers=headers, cookies=cookies, data=json.dumps(domainData))
print(response)
'''