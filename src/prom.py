import requests
import json
import time
import logging
from requests.auth import HTTPBasicAuth
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server, push_to_gateway, Gauge, CollectorRegistry
from prometheus_client.exposition import basic_auth_handler
from script.config import build_config
from script.logging_setup import custom_logging


logger = logging.getLogger(__name__)

conf = build_config()
PROM_URL = conf['prom_push_url']


class CustomCollector(object):
    
    def __init__(self, TAG):
        self.TAG = TAG
        
    def collect(self):
        try:
            with open('metrics.json') as f:
                data = json.load(f)
                domain_data = data.items()
                g = GaugeMetricFamily(
                    'ecom_asset_monitor_sum', 'Assets_failed_to_access', labels=['Assets', 'Brand','TLD','Version'])
                for k, v in domain_data:
                    domain = k
                    brand = domain.split(".")[0]
                    tld = domain.split(".")[1 : ]
                    tld = "_".join(tld)
                    
                    TOTAL = v['TOTAL']
                    PASS = v['PASS']
                    FAIL = v['FAIL']
                    g.add_metric(['TOTAL', brand,tld,self.TAG], TOTAL)
                    g.add_metric(['PASS', brand,tld,self.TAG], PASS)
                    g.add_metric(['FAIL', brand,tld,self.TAG], FAIL)
                yield g
        except OSError as e:
            logger.error(e)


def updateMetrics(TAG):
    registry = CollectorRegistry()
    registry.register(CustomCollector(TAG))
    try:
        push_to_gateway(PROM_URL, job='akamai-assets-monitoring', registry=registry)
    except Exception as e:
       logger.error(e)
