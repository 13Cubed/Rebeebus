# Rebeebus
**Rebeebus is an rDNS lookup utility. This script is very useful for parsing email headers, log files, and any other arbitrary data for IPv4 addresses, and then performing reverse DNS lookups for each of those addresses using the specified DNS server.**

For any given file(s), Rebeebus will:

- Extract valid IPv4 addresses (e.g., "CSI: Cyber" addresses like 951.27.9.840 will not match)
- Ignore duplicates
- Ignore bogon addresses, the loopback network, and link local addresses
- Optionally parse RFC 1918 (private) addresses

For each remaining address, Rebeebus will provide the following data as available:

**- IP Address, Hostname, Count**

By default, Rebeebus will display the data to stdout in the following format:

```
IP Address    | Hostname                                   | Count
52.73.116.225 | ec2-52-73-116-225.compute-1.amazonaws.com. | 5
```

- Using the "**-p**" option, Rebeebus will include RFC 1918 (private) addresses.

- Using the "**-w**" option, you can provide a filename to which Rebeebus will output the data in CSV format (useful for working with large data sets in Microsoft Excel or LibreOffice Calc):

```
IP Address,Hostname,Count
52.73.116.225,ec2-52-73-116-225.compute-1.amazonaws.com,5
```

- Using the "**-s**" option, Rebeebus will sort the addresses numerically by the first octet.

**Rebeebus uses the dnspython library, and is compatible with Python 2 and 3.**
