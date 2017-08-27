#This script will find the new IPs of domains to update the PostFix relay setting with
import socket
#import dns.resolver
import subprocess
import shlex


#Dyn Domain -- will change this to find the domain via some method that doesn't get over wrote via Git
domain = "'remote.imaqeo.com'"


#Let's scrap this way of doing it and find a simpler way

#def IPGrab(domain):
#    for rdata in dns.resolver.query( domain, 'CNAME') :
#        print(rdata.target)

def IPGrab(domain):
    cmd = "dig +short %d | sed -n 2p" % domain
    proc=subprocess.Popen(shlex.split(cmd),stdout=subprocess.PIPE)
    out,err=proc.communicate()
    print(out)


IPGrab(domain)
