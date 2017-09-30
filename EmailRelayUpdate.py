#This script will find the new IPs of domains to update the PostFix relay setting with
import socket
import dns.resolver
import subprocess
import shlex
import re

#Dyn Domain -- will change this to find the domain via some method that doesn't get over wrote via Git
domain = "'remote.imaqeo.com'"
path = "/etc/postfix/main.cf"


#Need to see if we can get this way of doing it to work. 

def IPGrab2(domain):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['8.8.8.8']
    resolver.port = 53
    for i in resolver.query(domain, 'A').response.answer:
        for j in i.items:
            print (j.to_text())
    
#The hard way
def IPGrab(dom):
    cmd = "dig +short %s" % dom
    proc=subprocess.Popen(shlex.split(cmd),stdout=subprocess.PIPE)
    out,err=proc.communicate()
    decode = out.decode("utf-8")
    #print(decode)
    #iplist = [s.strip() for s in out.splitlines()]
    #c = 0
    ips = re.findall( '\\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\b', decode)
    return ips
    #for i in iplist:
    #    cleanlist[c] = pattern.search(i)         
    #    print(cleanlist[c])
    #    c = c+1

def FileEditor():
    ipstring = ""
    for IP in IPGrab(domain):
        ipstring += IP + "/32,"
    print(ipstring)
    #Let's create the temp file
    temp = open("/tmp/emailrelay.tmp", "a")
    #Let's open the current file
    with open (path, 'rt') as in_file:
        #Now write each line individually to the new file. Looking for the 'mynetworks = ' line
        for line in in_file:
            if line.find("mynetworks =")==0:
                temp.write("mynetworks = %s\n" % ipstring)
            else:    
                temp.write(line)

    temp.close()

    #Do some house work
    cmd = "mv -f /tmp/emailrelay.tmp %s" % path
    proc=subprocess.Popen(shlex.split(cmd),stdout=subprocess.PIPE)
    out,err=proc.communicate()
    #print out to error log
    cmd = "rm -rf /tmp/emailrealy.tmp"
    proc=subprocess.Popen(shlex.split(cmd),stdout=subprocess.PIPE)
    out,err=proc.communicate()
    #print out to error log

    #for IP in IPGrab(domain):
     #   print(IP + "/32")


FileEditor()
#IPGrab(domain)
#IPGrab2(domain)
