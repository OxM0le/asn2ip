#!/usr/bin/python3

from optparse import OptionParser
import pyasn
import glob
import os
import subprocess
import inquirer
import re
import sys
from netaddr import *

##### Variables #####

##### Functions #####
#####Orgserach from asn.list
def orgsearch(orgname):
   results=[]
   pattern=orgname
   f = open("asn.list", "r")
   for line in f:
      line = line.strip()
      if re.search(pattern, line,re.IGNORECASE):
         results.append(line)
   if not results:
      print("The pattern could not be found, try again.") 
      exit(1)
   questions = [
     inquirer.List('entry',
                   message="What search term do you have in mind ?",
                   choices=results
               ),
   ]
   answers = inquirer.prompt(questions)
   return answers


#Options Parser
parser = OptionParser()
parser.add_option("-u", action="store_true", dest="db", help="create or update IPASN Data file ")
parser.add_option("-s", type=str, dest="org", help="search asn ip addresses based on search term")
(options, args) = parser.parse_args()

#Print help if no argument 
parser.parse_args(args=None if sys.argv[1:] else ['--help'])

#Update asndb with pyasn scripts
if options.db:
    #delete existing bz2 file in directory
    bzfile = glob.glob("*.bz2")
    if bzfile:
       for file in bzfile:
          os.remove(file)   
    subprocess.call("pyasn_util_download.py --latest", shell=True)
    bzfile = glob.glob("*.bz2")
    bzfile = bzfile[0] 
    convert = 'pyasn_util_convert.py --single' + ' ' + bzfile + ' ' + 'ipasndb' 
    subprocess.call(convert, shell=True)
    if bzfile:
          os.remove(bzfile)
    sys.exit(0)

#Get AS Value and queries subnets
if options.org:
   #Initiate ASN DB
   try:
      asndb = pyasn.pyasn('ipasndb')
   except:
      print("Please use \"asn2ip -u \" to create the required DB") 
      parser.print_help() 
      sys.exit(1)
   orgname = options.org
   #Search Orgname in file
   entry=orgsearch(orgname)
   values = list(entry.values())
   asn = values[0].split(' ',1)
   asnname = asn[0]
   txtfile = open(asnname + "-" + orgname + ".txt", "a")
   asn = asnname.lower().replace('as', '')
   prefixes = asndb.get_as_prefixes(asn)
   try:
      for prefix in prefixes:
         for ip in IPNetwork(prefix):
            txtfile.write('%s \n' %ip)
      txtfile.close()
      print("The required ip addresses can be found in " + asnname + "-" + orgname + ".txt")
   except:
      print("No prefixes for " + asnname + " could be found within the DB")
      os.remove(asnname + "-" + orgname + ".txt") 
      sys.exit(0)
 
