import requests
import json
import re
import logging
from requests.auth import HTTPBasicAuth
from script.config import build_config
from src.prom import updateMetrics
from script.logging_setup import custom_logging
import os
from urllib.parse import quote
import git
from git import Repo

custom_logging(logging.INFO)
logger = logging.getLogger(__name__)

def clone(username, Bit_token, Bit_repo):
    repo_path = "."
    git.Git(repo_path).clone(("https://" + username +
                             ":" + Bit_token + "@" + Bit_repo), branch='master')


Assetscount = {}
metrics = {}

conf = build_config()
if conf is None:
    logger.error('Make sure configs/config.ini has been setup properly')
USER = conf['username']
TOKEN = conf['token']
FILE = conf['file_name']
TOKEN = quote(TOKEN)
        
        
def availablity_check(data):   
    
    file_check = os.path.isfile("netstorage-assets/assets.txt")
    if file_check == True:
        with open('netstorage-assets/assets.txt') as asset_file:
            Assets_raw = asset_file.readlines()
            
        if "front-dist/react" not in Assets_raw[0]:
            logger.error('Jenkins assets.txt Returned BAD response')
            return
        Asset_one = Assets_raw[0]
        #print(Asset_one)
        TAG = Asset_one.split("/")[4]
        #print(TAG)
    
        Assetscount = {}
        metrics = {} 
        domain_data = data
        for k in domain_data:
            domain = k.strip("\n")
            PASS = 0
            FAIL = 0
            folder_check="na"
            n=0
            Assetscount = {}
            metrics = {}
            for asset in Assets_raw:
                asset=asset.strip("\n")
                asset_strip = asset.replace(
                    'data/front-dist/', '').strip(" ")
                if "react" in asset_strip:
                    try:
                        URL = "https://www." + domain + "/glass" + asset_strip
                        if n <= 7:
                            folder=asset_strip.split("/")[-2]
                            GET_REQUEST = requests.get(URL)
                            CODE = GET_REQUEST.status_code
                            n += 1
                            if CODE == 200:
                                PASS += 1
                                #print(URL)
                            else:
                                FAIL += 1
                                logger.error('400 status code for ' + URL)
                        else:
                            PASS += 1
                            folder_check=asset_strip.split("/")[-2]
                            if folder != folder_check:
                                n=0                                   
                    except requests.exceptions.RequestException as e:
                        logger.error(e)
            TOTAL = PASS + FAIL
            Assetscount['TOTAL'] = TOTAL
            Assetscount['PASS'] = PASS
            Assetscount['FAIL'] = FAIL
            metrics[domain] = Assetscount
            
            def write_json(data, filename='metrics.json'):
                with open("metrics.json", "w") as Count_metrics:
                    json.dump(data, Count_metrics, indent=4)
        
        
            with open('metrics.json') as json_file:
                data = json.load(json_file)
                data.update(metrics)
            
            write_json(data)
            updateMetrics(TAG)
    else:
        logger.error('assets.txt does not exists')    


if __name__ == '__main__':
    TAG = 0
    try:
        Bit_repo="https://localhost:7990/scm/netstorage-assets.git"
        Bit_repo_name = "netstorage-assets"
        clone(USER, TOKEN, Bit_repo)
        with open('domain.txt') as fr:
            data = fr.readlines()
        availablity_check(data)
    except OSError as e:
        logger.error(e)
