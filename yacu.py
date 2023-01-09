#!/usr/bin/env python

import os
import sys
import requests
import socket
import CloudFlare

os.environ['c_token'] = 'ER7d6OC-_x14TqZNcNiPNstOFse4phW-4aVUrlTN'
os.environ['c_hostname'] = 'cloud.stojanovski.me'

# MANDATORY_ENV_VARS = ["c_token", "c_hostname"]

# for var in MANDATORY_ENV_VARS:
#     if var not in os.environ:
#         raise EnvironmentError("Failed because {} is not set.".format(var))

def get_ip():
    url = 'https://ipinfo.io/ip'

    try:
        ip_address = requests.get(url).text
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    
    return ip_address

def compare_ip(hostname):
    # resolve the hostname with DNS and compare the IPs.
    dns_ip = socket.gethostbyname(hostname)

    print(dns_ip)
    print(get_ip())

    return (dns_ip == get_ip())

def update_dns(token, hostname):
    cf = CloudFlare.CloudFlare(token=token)
    zone_name = '.'.join(hostname.split(".")[-2:])
    
    try:
        params = {'name':zone_name}
        zones = cf.zones.get(params=params)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        exit('/zones %d %s - api call failed' % (e, e))
    except Exception as e:
        exit('/zones.get - %s - api call failed' % (e))
    
    # print(zones)

    if len(zones) == 0:
        exit('Zone not found: {}'.format(zone_name))
    
    zone = zones[0]
    params = {'name':hostname, 'match':'all'}
    dns_record = cf.zones.dns_records.get(zone['id'], params=params)[0]

    dns_update = {
            'name':hostname,
            'type':"A",
            'content':get_ip(),
            'ttl':60
    }

    try:
        cf.zones.dns_records.put(zone['id'], dns_record['id'], data=dns_update)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        exit('/zones.dns_records.put %s - %d %s - api call failed' % (hostname, e, e))
    print('UPDATED: {} -> {}'.format(hostname, get_ip()))

    # print(dns_record)
    return True

# print(compare_ip(os.environ.get('c_hostname')))

if not compare_ip(os.environ.get('c_hostname')):
    update_dns(os.environ.get('c_token'), os.environ.get('c_hostname'))
else:
    print("The IP is up to date")
