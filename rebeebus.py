#!/usr/bin/python
# rebeebus.py 1.0 - An rDNS lookup utility.
# Compatible with Python 2 and 3
# Copyright 2018 13Cubed. All rights reserved. Written by: Richard Davis

import sys
import json
import re
import csv
import argparse
import socket
import operator

# Handle Python 2 and 3 compatibility for urllib
try:
  from urllib.request import urlopen
except ImportError:
  from urllib2 import urlopen

# Import dns.resolver module and handle error on failure
try:
  import dns.resolver
except:
  print('Rebeebus requires the dns.resolver module. Please install it and try again.\nHint: pip install dnspython')
  sys.exit(1)

# Import dns.reversename module and handle error on failure
try:
  import dns.reversename
except:
  print('Rebeebus requires the dns.reversename module. Please install it and try again.\nHint: pip install dnspython')
  sys.exit(1)

def getData(filenames, dnsServer, includePrivate, sortByCount):
  """
  The given file is scraped for IPv4 addresses, and the addresses are used
  to attempt rDNS queries to the specified server.
  """

  addresses = []
  filteredAddresses = []
  results = []

  for filename in filenames:
    try:
      f = open(filename, 'rU')
    except IOError:
      print ('Could not find the specified file:', filename)
      sys.exit(1)

    # Parse file for valid IPv4 addresses via RegEx
    addresses += re.findall(r'(\b(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\b)',f.read())
    f.close()

  # Count number of occurrences for each IP address
  addressCounts = {i:addresses.count(i) for i in addresses}

  # Remove duplicates from list
  addresses = set(addresses)

  for address in addresses:
    if (includePrivate == 1):
      # Filter list to eliminate bogon addresses, the loopback network, and link local addresses; add results to new list
      if not (re.match(r'^0.\d{1,3}.\d{1,3}.\d{1,3}$|^127.\d{1,3}.\d{1,3}.\d{1,3}$|^169.254.\d{1,3}.\d{1,3}$', address)):
        filteredAddresses.append(address)
    else:
      # Filter list to eliminate bogon addresses, the loopback network, link local addresses, and RFC 1918 ranges; add results to new list
      if not (re.match(r'^0.\d{1,3}.\d{1,3}.\d{1,3}$|^127.\d{1,3}.\d{1,3}.\d{1,3}$|^169.254.\d{1,3}.\d{1,3}$|^10.\d{1,3}.\d{1,3}.\d{1,3}$|^172.(1[6-9]|2[0-9]|3[0-1]).[0-9]{1,3}.[0-9]{1,3}$|^192.168.\d{1,3}.\d{1,3}$', address)):
        filteredAddresses.append(address)

  # Configure the DNS resolver
  resolver = dns.resolver.Resolver()
  resolver.nameservers = [dnsServer]
  resolver.timeout = 1
  resolver.lifetime = 1

  # Iterate through new list and perform rDNS lookups
  for filteredAddress in filteredAddresses:
    formattedData = ''

    try:
      addr = dns.reversename.from_address(filteredAddress)
      formattedData = filteredAddress + ',' + str(resolver.query(addr,"PTR")[0]) + ','

    except:
      formattedData = filteredAddress + ',-,'

    # Get number of occurrences for IP address and add to results
    addressCount = addressCounts[filteredAddress]
    formattedData += str(addressCount)

    # Add final formatted data string to list
    results.append(formattedData)

  if (sortByCount == 1):
  	# Sort addresses by count (descending)
  	results	 = sorted(results, key=lambda x: int(x.split(',')[2]), reverse=True)

  # Add column headers
  results.insert(0,'IP Address,Hostname,Count')

  return results

def printData(results):
  rows = list(csv.reader(results))
  widths = [max(len(row[i]) for row in rows) for i in range(len(rows[0]))]

  for row in rows:
    print(' | '.join(cell.ljust(width) for cell, width in zip(row, widths)))

def writeData(results,outfile):
  try:
    f = open(outfile, 'w')
  except IOError:
    print ('Could not write the specified file:', outfile)
    sys.exit(1)

  for result in results:
    f.write(result + '\n')

  f.close()

def checkServer(dnsServer):
  # Configure the DNS resolver
  resolver = dns.resolver.Resolver()
  resolver.nameservers = [dnsServer]
  resolver.timeout = 1
  resolver.lifetime = 1

  try:
    answer = resolver.query('google.com', 'A')
    success = 1
  except dns.resolver.Timeout:
    success = 0

  return success

def main():
  parser = argparse.ArgumentParser(description='Rebeebus - An rDNS lookup utility.', usage='rebeebus.py filename(s) [-d x.x.x.x] [-p] [-w outfile] [-s]', add_help=False)
  parser.add_argument('filenames', nargs="*")
  requiredArguments = parser.add_argument_group('required arguments')
  requiredArguments.add_argument('-d','--dns-server', help='Use the specified DNS server to resolve addresses', required=True)
  parser.add_argument('-p', '--include-private', action='store_true', help='Attempt rDNS lookups for RFC 1918 (private) addresses', required=False)
  parser.add_argument('-w', '--write', help='Write output to CSV file instead of stdout', required=False)
  parser.add_argument('-s', '--sort', action='store_true', help='Sort addresses by count (descending)', required=False)
  parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit')
  args = vars(parser.parse_args())

  # Make sure at least one filename was provided
  if not (args['filenames']):
    parser.print_usage()
    parser.exit()

  filenames = args['filenames']
  includePrivate = 0
  writeToFile = 0
  sortByCount = 0

  if (args['dns_server']):
    # Validate provided server IP address
    try:
      socket.inet_aton(args['dns_server'])
      dnsServer = args['dns_server']
    except socket.error:
      parser.print_usage()
      parser.exit()

  if (args['include_private']):
    includePrivate = 1

  if (args['write']):
    writeToFile = 1
    outfile = args['write']

  if (args['sort']):
    sortByCount = 1

  # Let's make sure the specified DNS server is working before we go any further ...
  success = checkServer(dnsServer)
  if (success == 0):
    print(str(dnsServer) + ' is not responding to DNS queries. Are you sure that\'s the correct IP address?')
    sys.exit(1)

  output = getData(filenames,dnsServer,includePrivate,sortByCount)

  if (writeToFile == 1):
    writeData(output,outfile)

  else:
    printData(output)

  print ('\nCopyright (C) 2018 13Cubed. All rights reserved.')

if __name__ == '__main__':
  main()
