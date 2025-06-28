#!/usr/local/bin/python3
from __future__ import print_function

import sys
import json
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# pip3 install requests
# pip3 install bs4
# pip3 install html5lib
# pip3 install lxml

admin_username = 'admin'
admin_password = 'Wiz2025$1!'
index_post_import = 'true' # if you want to trigger a reindex immediately after the space import (false if you don't)
confluence_base_url = 'https://rsconf.realsenseai.com'
file = 'space/Confluence-space-export-SW1-2025-04-01-07-18-53-710.xml_fixed.zip' # here you put only the export file name, without any path (it needs to reside inside the <confluence-shared-home/restore directory)
status_refresh_interval=0.5 # refresh rate (in seconds) for the space import status request

def print_statusline(msg: str):
    last_msg_length = len(print_statusline.last_msg) if hasattr(print_statusline, 'last_msg') else 0
    print(' ' * last_msg_length, end='\r')
    print(msg, end='\r')
    print_statusline.last_msg = msg

def get_authenticated_admin_session_and_token():
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': '*/*'}
    url = confluence_base_url+'/doauthenticate.action'
    session = requests.Session()
    # retrieve the session cookies
    try:
        print("[ %s ] INFO Authenticating with Confluence ..." % (datetime.now().strftime("%Y/%m/%d %H:%M:%S")))
        session.post(confluence_base_url + '/users/viewmyprofile.action', auth = (admin_username, admin_password), headers = headers)

        # retrieve the ATL_TOKEN
        try:
            print("[ %s ] INFO Retrieving the ATL_TOKEN ..." % (datetime.now().strftime("%Y/%m/%d %H:%M:%S")))
            r = session.post(url, headers = headers)
            soup_token = BeautifulSoup(r.text, "lxml")
            atlassian_token = soup_token.find("meta", {"id": "atlassian-token"})["content"]
            space_import(session, atlassian_token)
        except Exception as e:
            print("[ %s ] ERROR ATL_TOKEN retrieval failed: [%s]" % (datetime.now().strftime("%Y/%m/%d %H:%M:%S"), str(e)))
            sys.exit(1)

    except Exception as e:
        print("[ %s ] ERROR Authentication failed: [%s]" % (datetime.now().strftime("%Y/%m/%d %H:%M:%S"), str(e)))
        sys.exit(1)

def space_import(session, atlassian_token):
    payload = {'atl_token':atlassian_token, 'localFileName':file, 'buildIndexLocalFileRestore':index_post_import, 'edit':'Import'}
    
    # testers
    print (payload)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    url = confluence_base_url + '/admin/restore-local-file.action'
    try:
        print("[ %s ] INFO Starting the space import [file: <shared_home>/restore/%s] [index rebuild post-import set to %s] ..." % (datetime.now().strftime("%Y/%m/%d %H:%M:%S"), file, index_post_import))
        i = session.post(url, headers = headers, data = payload)

        try:
            soup_import = BeautifulSoup(i.text, "lxml")
            check_error = soup_import.find('div', attrs = {'class':'aui-message aui-message-error closeable'})

            if check_error is not None:
                import_error = check_error.get_text()
                print("[ %s ] ERROR Import failed: [%s]" % (datetime.now().strftime("%Y/%m/%d %H:%M:%S"), import_error.replace('\n', ' ').replace('.', '').lstrip().rstrip()))
                sys.exit(1)
            else:
                headers = {'Content-Type': 'application/json', 'Accept': '*/*'}


                task_id = soup_import.find("meta", {"name": "ajs-taskId"})["content"]
                url = confluence_base_url + '/rest/api/longtask/' + task_id

                percentage_complete = 0
                while percentage_complete < 100:
                    try:
                        s = session.get(url, headers = headers)
                        s_dict = json.loads(s.text)
                        status = s_dict['messages'][0]['translation']
                        percentage_complete = s_dict['percentageComplete']
                        elapsed_time = round(s_dict['elapsedTime'] / 1000, 2)

                        output = 'Space import status: [' + str(status) + '] [' + str(percentage_complete) + '%]'

                        print_statusline(output)
                        time.sleep(status_refresh_interval)

                    except Exception as e:
                        print("[ %s ] WARN Error when getting the space import status: [%s]" % (datetime.now().strftime("%Y/%m/%d %H:%M:%S"), str(e)))
                        continue

            print('', end = '\n', flush = True)
            print("[ %s ] INFO Space import finished in [%s] seconds!" % (datetime.now().strftime("%Y/%m/%d %H:%M:%S"), elapsed_time))

        except Exception as e:
            print("[ %s ] ERROR Import failed: [%s]" % (datetime.now().strftime("%Y/%m/%d %H:%M:%S"), str(e)))
            sys.exit(1)

    except Exception as e:
        print("[ %s ] ERROR Space import failed (HTTP request): [%s]" % (datetime.now().strftime("%Y/%m/%d %H:%M:%S"), str(e)))
        sys.exit(1)

get_authenticated_admin_session_and_token()

