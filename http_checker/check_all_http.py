#!/usr/bin/env python3
# -*- coding:  utf-8 -*-

import time
import pycurl
import sys,os 
import math
import socket


devnull = open(os.devnull, 'wb')

if "CHECK_SOURCE" in os.environ:
    check_source = os.environ['CHECK_SOURCE']
    if check_source == "":
        check_source = socket.gethostname()    
else:
    check_source = socket.gethostname()


def write_to_file(message):
    text_file = open("data/http_response_time_ms.prom", "w")
    text_file.write(message)
    text_file.close()

def py_curl(checked_url):
    c = pycurl.Curl()
    c.setopt(pycurl.URL, checked_url)              #set url
    c.setopt(pycurl.FOLLOWLOCATION, 1)  
    c.setopt(pycurl.USERAGENT, "HSM Checker")
    c.setopt(c.WRITEDATA, devnull)
    try: 
        content = c.perform()                        #execute 
    except Exception: 
       
        dns_time = -1
        conn_time = -1
        starttransfer_time = -1
        total_time = -1

    else: 
        dns_time = c.getinfo(pycurl.NAMELOOKUP_TIME) #DNS time
        conn_time = c.getinfo(pycurl.CONNECT_TIME)   #TCP/IP 3-way handshaking time
        starttransfer_time = c.getinfo(pycurl.STARTTRANSFER_TIME)  #time-to-first-byte time
        total_time = c.getinfo(pycurl.TOTAL_TIME)  #last requst time

    c.close()
    return dns_time, conn_time, starttransfer_time, total_time

header = """# HELP http_response_time_ms The HTTPS response time single page in miliseconds
# TYPE http_response_time_ms gauge
"""
urllist = open("url.list", 'r')
urls=urllist.readlines()
urllist.close()

check_results=[]

while 1 == True:
    
    for url in urls:
        url=url.replace("\n","")
        dns_time, conn_time, starttransfer_time, total_time = py_curl(url)
        dns_time=round(dns_time, 4)
        conn_time=round(conn_time, 4)
        starttransfer_time=round(starttransfer_time, 4)
        total_time=round(total_time, 4)
        check_item="http_response_dns_time_ms{domain=\""+url+"\", source=\""+check_source+"\"} "+str(dns_time)+"\nhttp_response_conn_time_ms{domain=\""+url+"\", source=\""+check_source+"\"} "+str(conn_time)+"\nhttp_response_starttransfer_time_ms{domain=\""+url+"\", source=\""+check_source+"\"} "+str(starttransfer_time)+"\nhttp_response_total_time_ms{domain=\""+url+"\", source=\""+check_source+"\"} "+str(total_time)+"\n"
      
        check_results.append(check_item)

# join list to one string    
    string_results = '\n'.join(check_results)
    full_text=header+string_results
    write_to_file(full_text)
    del check_results[:]
    time.sleep(10)

