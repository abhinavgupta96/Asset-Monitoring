import requests
import json
import re
import logging
from requests.auth import HTTPBasicAuth
from script.logging_setup import custom_logging
from datetime import datetime
import time
import git
from git import Repo
import os
import shutil
import filecmp
from urllib.parse import quote


custom_logging(logging.INFO)
logger = logging.getLogger(__name__)

Assetscount = {}
metrics = {}


DEPLOY_URL = "https://localhost:8001/job/deploy-assets-netstorage/"

PRODUCTION_JENKINS = "https://localhost:8001/job/production/lastSuccessfulBuild/console"
PATTERN=r"job\/deploy-assets-netstorage\/\d+"
        
        
def fetch(USER,TOKEN):
    try:
        prod_response = requests.get(PRODUCTION_JENKINS, auth=HTTPBasicAuth(USER, TOKEN))
        concole = prod_response.content.decode('utf-8')
        #print(prod_response,concole)
        prod_status = prod_response.status_code
        if prod_status != 200:
            logger.error('Jenkins Production Job Returned BAD response')
            return 
        else:
            logger.error('Jenkins Production Job Returned 200')
            result = re.search(PATTERN, concole)
            #print(result)
            job=result.group(0)
            #print(job)
            buildnumber=job.split("/")[-1]
            print(buildnumber)
                
    except requests.exceptions.RequestException as e:
            logger.error(e)
    try:
        #JEN_URL = DEPLOY_URL + buildnumber + FILE
        JEN_URL="https://localhost:8001/job/deploy-assets-netstorage/"+ str(buildnumber) + "/artifact/assets.txt"
        #print(JEN_URL)
        response = requests.get(JEN_URL, auth=HTTPBasicAuth(USER, TOKEN))
        Assets_raw = response.content.decode('utf-8')
        jen_status = response.status_code
        #print(Assets_raw)
        with open('assets.txt','w') as asset_file:
            asset_file.write(Assets_raw)
        if jen_status != 200 or "front-dist/react" not in Assets_raw:
            logger.error('Jenkins assets.txt Returned BAD response')
            return
        logger.error('Jenkins Job Returned 200')
    except requests.exceptions.RequestException as e:
        logger.error(e)
        


def clone(USER,TOKEN, Bit_repo):
    repo_path = "."
    git.Git(repo_path).clone(("https://" + USER +
                             ":" + TOKEN + "@" + Bit_repo), branch='master')


def push_to_git(Bit_repo_name):
    filename = 'assets'
    web_check = os.path.isfile(Bit_repo_name + "/" + filename + ".txt")
    file_modified = filecmp.cmp('assets.txt', 'netstorage-assets/assets.txt')

    if not file_modified:
        shutil.copy(filename + '.txt', Bit_repo_name + "/" + filename + ".txt")
        repo = git.Repo(Bit_repo_name)
        repo.git.add('assets.txt')
        repo.git.commit('-m', 'Updated-file-at-' + str(time.time()))
        origin = repo.remote(name='origin')
        origin.push()
        try:
            shutil.rmtree(Bit_repo_name)
        except OSError as e:
            result = "no such file"
        return True
    else:
        try:
            shutil.rmtree(Bit_repo_name)
            logger.error("no changes found in assests file")
        except OSError as e:
            result = "no such file"
        return False

if __name__ == '__main__':
    TAG = 0
    try:
        TOKEN = os.getenv("TOKEN")
        BIT_TOKEN=quote(os.getenv("TOKEN"))
        USER = os.getenv("USER")
        fetch(USER,TOKEN)
        Bit_repo="https://localhost:7990/scm/netstorage-assets.git"
        Bit_repo_name = "netstorage-assets"
        clone(USER, BIT_TOKEN, Bit_repo)
        push_to_git(Bit_repo_name)
    except OSError as e:
        logger.error(e)
