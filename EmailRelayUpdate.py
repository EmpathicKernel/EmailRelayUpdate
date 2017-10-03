#This script will find the new IPs of domains to update the PostFix relay setting with
import socket
#import dns.resolver
import subprocess
import shlex
import re
import time

#Dyn Domain -- will change this to find the domain via some method that doesn't get overwrote via Git
domain = "'remote.imaqeo.com'"
path = "/etc/postfix/main.cf"



#Bash command function
def excomm(com):
    proc=subprocess.Popen(shlex.split(com),stdout=subprocess.PIPE)
    out,err=proc.communicate()
    output=out.decode("utf-8")
    return output
    #We need to do something with any errors

#Grab the IP from a dig
def IPGrab(dom):
    decode = excomm("dig +short %s" % dom)
    ErrorHandler("Dig result of %s" % dom + " is: %s" % decode)
    ips = re.findall( '\\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\b', decode)
    return ips

def FileEditor():
    ipstring = ""
    ips=IPGrab(domain)
    if len(ips) == 1:
        ipstring += ips[0] + "/32"
    else:
        c = 1
        for IP in ips:
            if c < len(ips):
                ipstring += IP + "/32,"
                c += 1
            else:
                ipstring += IP + "/32"
                c += 1
        
    ErrorHandler("New IP string is %s" % ipstring)
    #Let's create the temp file
    temp = open("/tmp/emailrelay.tmp", "a")
    #Let's open the current file
    with open (path, 'rt') as in_file:
        #Now write each line individually to the new file. Looking for the 'mynetworks = ' line
        for line in in_file:
            if line.find("mynetworks =")==0:
                if line.find("#")!=0:
                    temp.write("mynetworks = %s\n" % ipstring)
            else:    
                temp.write(line)

    temp.close()

    e1 = excomm("mv -f /tmp/emailrelay.tmp %s" % path)
    if e1 == "":
        ErrorHandler("No error during overwrite of temp file to %s" % path)
    else:
        ErrorHandler(e1)
    #print out to error log
    e2 = excomm("rm -rf /tmp/emailrealy.tmp")
    #print out to error log
    if e2 == "":
        ErrorHandler("No error doing removal of /tmp/emailrealy.tmp")
    else:
        ErrorHandler(e2)
    #for IP in IPGrab(domain):
     #   print(IP + "/32")
def ErrorHandler(err):
    ef = open("/var/log/EmailRelayUpdate.log", "a")
    #error = datetime.datetime + " -- " + err
    ef.write(time.strftime("%m/%d/%Y:%H:%M:%S") + " -- " + err + "\n")
    ef.close()


FileEditor()
