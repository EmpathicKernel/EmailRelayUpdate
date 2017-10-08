#This script will find the new IPs of domains to update the PostFix relay setting with
import os.path
import subprocess
import shlex
import re
import time

#Initilizing the globals
#
#'domain' is the domain that we set in the settings.config file. This is the dynamic domain we are querying
#'path' is the path to the PostFix main.cf file. This is read from the settings.config file
domain = ""
path = ""



#Bash command function
#
#INPUT: String
#INPUT is a command that is to be ran in bash
#OUTPUT: String
#OUTPUT is the result of INPUT in a String format
def excomm(com):
    proc=subprocess.Popen(shlex.split(com),stdout=subprocess.PIPE)
    out,err=proc.communicate()
    output=out.decode("utf-8")
    return output

#Grab the IP from a dig
#
#INPUT: NONE
#OUTPUT: String
#OUTPUT is the string of IPs that is returned from the DIG
def IPGrab():
    decode = excomm("dig +short %s" % domain)
    ErrorHandler("Dig result of %s" % domain + " is: %s" % decode) #Need to write this to the error log in case anything is captured. Also helps in troubleshooting
    ips = re.findall( '\\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\b', decode) #We're only looking for IPs
    return ips

#Main
#INPUT: NONE
#OUTPUT: NONE
#This is the main function that also modifies the main.cf file
def FileEditor():
    ipstring = ""
    ips=IPGrab()
    if len(ips) == 1:
        ipstring += ips[0] + "/32" #Don't want a comma if it's only one IP
    else: #Otherwise we go through and add commas until the last IP
        c = 1
        for IP in ips:
            if c < len(ips):
                ipstring += IP + "/32,"
                c += 1
            else:
                ipstring += IP + "/32"
                c += 1
        
    ErrorHandler("New IP string is %s" % ipstring) #Need to write this to error log for troubleshooting

    temp = open("/tmp/emailrelay.tmp", "a") # Creating a temp file so the main.cf file has less chance to disappear

    with open (path, 'rt') as in_file:
        #Now write each line individually to the new file. Looking for the 'mynetworks = ' line
        for line in in_file:
            if line.find("mynetworks =")==0:
                if line.find("#")!=0: #Don't want commented lines
                    temp.write("mynetworks = %s\n" % ipstring)
            else:    
                temp.write(line)

    temp.close() #Close the temp file

    #Now lets start cleaning house with our temp file
    e1 = excomm("mv -f /tmp/emailrelay.tmp %s" % path) #Let's overwrite the main.cf file with our temp file
    if e1 == "":
        ErrorHandler("No error during overwrite of temp file to %s" % path) #There are no errors but need troubleshoot tracking
    else:
        ErrorHandler(e1) #There is an error so lets log it
    e2 = excomm("rm -rf /tmp/emailrealy.tmp") #Let's remove our temp file
    if e2 == "":
        ErrorHandler("No error doing removal of /tmp/emailrealy.tmp") #There are no errors but need troubleshoot tracking
    else:
        ErrorHandler(e2) #There is an error so lets log it

#Error Handling
#INPUT: String
#INPUT is the string to write to the error log
#OUTPUT: NONE
#Errors are written to /var/log/EmailRelayUpdate.log
def ErrorHandler(err):
    ef = open("/var/log/EmailRelayUpdate.log", "a")
    ef.write(time.strftime("%m/%d/%Y:%H:%M:%S") + " -- " + err + "\n") #Let's write the error
    ef.close()

#Grabing of the globals
#INPUT: NONE
#OUTPUT: NONE
def SetConfig():
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    settings = os.path.join(__location__, 'settings.config')
    with open (settings, 'rt') as config:
        ErrorHandler("Opening %s" % settings)
        for line in config:
            if line.find("#")!=0:
                if line.find("DOMAIN:")==0:
                    domain = line[7:]
                if line.find("POSTFIX:")==0:
                    path = line[8:]


SetConfig()
FileEditor()
