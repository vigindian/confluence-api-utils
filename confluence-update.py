#!/usr/bin/env python3

import json
import requests

import sys #error-handling

#handle script arguments
import argparse

#password handling with keyring
import getpass
import keyring

#trigger bash script
from subprocess import call

headers = {
   "Accept": "application/json",
   "Content-Type": "application/json"
}

############
# FUNCTIONS
############
def get_login(username = None, passwd = None):

    if username is None:
        username = getpass.getuser()

    #passwd = keyring.get_password('confluence_script', username)
    if passwd is None:
        passwd = getpass.getpass()
        keyring.set_password('confluence_script', username, passwd)

    return (username, passwd)

def get_page_ancestors(auth, pageid):
# Get basic page information plus the ancestors property

    url = '{base}/{pageid}?expand=ancestors'.format(
        base = baseUrl,
        pageid = pageid)

    r = requests.get(url, auth = auth) 

    r.raise_for_status()

    return r.json()['ancestors']

def get_page_info(auth, pageid):

    url = '{base}/{pageid}'.format(
        base = baseUrl,
        pageid = pageid)

    r = requests.get(url, auth = auth)

    r.raise_for_status()

    return r.json()

def write_data(auth, html, pageid, title = None):

    info = get_page_info(auth, pageid)

    ver = int(info['version']['number']) + 1

    ancestors = get_page_ancestors(auth, pageid)

    anc = ancestors[-1]
    del anc['_links']
    del anc['_expandable']
    del anc['extensions']

    if title is not None:
        info['title'] = title

    data = {
        'id' : str(pageid),
        'type' : 'page',
        'title' : info['title'],
        'version' : {'number' : ver, 'minorEdit' : True, 'message' : 'Updated by automation'},
        'ancestors' : [anc],
        'body'  : {
            'storage' :
            {
                'representation' : 'storage',
                'value' : str(html),
            }
        }
    }

    data = json.dumps(data)

    url = '{base}/{pageid}'.format(base = baseUrl, pageid = pageid)

    r = requests.put(
        url,
        data = data,
        auth = auth,
        headers = headers
    )

    r.raise_for_status()

    print ("Wrote '%s' version %d" % (info['title'], ver))
    print ("URL: %s%d" % (viewUrl, pageid))

def main():

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
        "-t",
        "--title",
        default = None,
        type = str,
        help = "Specify a new title")

    parser.add_argument(
        "-f",
        "--file",
        default = None,
        required = True,
        type = str,
        help = "Write the contents of FILE to the confluence page")

    parser.add_argument(
        "pageid",
        type = int,
        help = "Specify the Conflunce page id to overwrite")

    options = parser.parse_args()

    siteurl = options.site

    global baseUrl
    global viewUrl 
    baseUrl = siteurl + "/wiki/rest/api/content"
    viewUrl = siteurl + "/wiki/pages/viewpage.action?pageId="

    #validate confluence-site-url input syntax
    if not siteurl.startswith("https://"):
        sys.exit("ERR: site url must start with 'https://'. Example: https://kansvignesh.atlassian.net")

    #if token key_ring is used - uncomment below
    #auth = get_login(options.user, options.password)

    #username and password is given as script input
    auth = (options.user, options.password)

    with open(options.file, 'r') as fd:
        html = fd.read()

    write_data(auth, html, options.pageid, options.title)

#######
# MAIN
#######
if __name__ == "__main__" : main()
