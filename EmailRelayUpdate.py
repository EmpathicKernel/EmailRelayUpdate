#This script will find the new IPs of domains to update the PostFix relay setting with
import socket
import dns.resolver



#Dyn Domain -- will change this to find the domain via some method that doesn't get over wrote via Git
domain = "'remote.imaqeo.com'"

IPGrab(domain)

def IPGrab(domain):
    for rdata in dns.resolver.query( domain, 'CNAME') :
        print(rdata.target)
