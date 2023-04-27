#!/usr/bin/env python3

import json
import requests

import sys #error-handling

#store in keyring
import keyring

#process input arguments
import argparse

#get username/password from user-prompt if not passed as argument
import getpass

###########
# FUNCTION
###########
def get_page_json(page_id, expand = False):
    if expand:
        suffix = "?expand=" + expand
                              #body.storage
    else:
        suffix = ""

    #url="https://yourdomain.atlassian.net/wiki/rest/api/content/" + page_id + suffix
    url=siteurl + "/wiki/rest/api/content/" + page_id + suffix
    response = requests.get(url, auth=(username,password))
    response.encoding = "utf8"

    try:
        resptext = json.loads(response.text)
    except:
        resptext = None

    return resptext

#######
# MAIN
#######

#get password from keyring
#password = keyring.get_password('confluence_script', username)

parser = argparse.ArgumentParser()

parser.add_argument(
        "-u",
        "--user",
        required = True,
        default = getpass.getuser(),
        help = "Specify the username to log into Confluence")

parser.add_argument(
        "-p",
        "--password",
        required = True,
        type = str,
        default = None,
        #prompt user for password - uncomment below line
        #default = getpass.getpass(),
        help = "Specify the api-key to access Confluence")

parser.add_argument(
        "-s",
        "--site",
        type = str,
        required = True,
        default = None,
        help = "Specify the Conflunce site URL")

parser.add_argument(
        "pageid",
        type = int,
        help = "Specify the Conflunce page id to read")

options = parser.parse_args()

username=options.user
password=options.password
pageid=options.pageid
siteurl=options.site

if not siteurl.startswith("https://"):
  sys.exit("ERR: site url must start with 'https://'. Example: https://kansvignesh.atlassian.net")

if password is None:
  password = getpass.getpass()
  keyring.set_password('confluence_script', username, password)

#print(get_page_json(pageid, "body.view"))
getPageDetails = get_page_json(str(pageid), "body.storage")
print(getPageDetails)
