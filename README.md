# procsock / procsocksh

A simple tool to enumerate all sockets on a host and map them to their full argv values

## Usage

### procsocksh

The procsocksh tool is a data gathering tool, written as a simple shellscript. It is meant to be run from a central "admin" host, a machine that has SSH private keys to access many other hosts. The script uses an input file, consisting of IP addresses, and serially logs in to each machine, executes the command (without alocating a pty) and redirects output to the local system, into a specially named file. It is meant to be run against a large amount of hosts. It retrieves the output from the following commands:

* ```lsof +c 0 -i4 -P -n -Fn -Fp -FT -F0```
* ```ps -e -o pid= -o user= -o comm= -o args=```

The data retrieved is processed later by procksock

### procsock

The procksock tool is written in Python and contains logic to join up the lsof and ps data such that given an IP and port, the user can quickly identify exactly what executable is running. For stability, you should use a Python virtual environment. One is built for you if you run make.

```
$ make
$ source venv/bin/activate
$ ./procsock -d testcase_in
$ cat output.json
...
```

Note the format of the testcase_in data. This *must* be data created by procksocksh as the filenames are parsed using regex. The flags to ps and lsof are also extremely important.

## Suggested uses

This tool is most useful in enriching the results of a large port scans that are conducted regularly. A small web interface showing IP address and open ports, a network service banner, and the process name is a very valuable piece of data and helps in identifying vulnerable services, either proactively or in response to a high severity security advisory. Examples: perform a search for "tomcat" or "haproxy"...

## Notes

This data is meant to be ingested into a database, alongside port scan data. It is then meant to be consumed via a web application.

## Author

copyright [at] mzpqnxow.com

## License

Copyright (C) 2017 copyright@mzpqnxow.com under the MIT license
Please see COPYRIGHT for terms
