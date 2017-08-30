# -*- coding: utf-8 -*-
""" LSOF class, a parallelized class for processing lsof output into a dict

Copyright (C) 2017 copyright /at/ mzpqnxow.com under the MIT license
Please see COPYRIGHT for terms
"""
from __future__ import print_function
from collections import defaultdict
from proclib.worker import ProcToolWorker


class LSOF(ProcToolWorker):
    """
        A parallellized lsof output parser

        Input:
            Path to lsof results files. This data is produced by procsocksh
            and must be formatted and named in a certain way

        Output:
            A dictionary with key (ip, pid) containing process information for
            all listening sockets. This can be merged with ps output for more
            complete info.

        Notes:
            By default, it will paralellize into CPU count + 1 because this can
            be very slow depending on how many files you have to process.

            The system CPU count is acquired via POSIX sysconf()
    """
    all_records = {}

    def __init__(self, results_path, cmd, extension='.ret.complete'):
        super(self.__class__, self).__init__(
            results_path, cmd, extension=extension)

    def load(self, completed, queue):
        """ Parse lsof -F0 output into dictionaries

        Input:
               Output of 'lsof +c 0 -i4 -P -n -Fn -Fp -FT -F0' in files

        Output:
               None, populate _lsof_records

        Notes:

               Output from lsof -F0 is a repeating set a of 'p' lines, where a
               'p' line contains NULL delimited information about a process,
               i.e. pid, userid, process name, etc.) and then 0 or more sets of
               'f' lines which contain fields describing a file descriptor,
               also NULL byte delimited. Examples for fields on a field include
               things like 'TST' for TCP State, 'P' for protocol, 'n' for
               interface and port, etc. All TCP fields are themselves delimited
               by '=', for example, 'TST=LISTEN'. It looks roughly like this:

               p3015\x00g3015\x00R2764\x00csquid\x00u99\x00Lnobody
               f5\x00a\x00u\x00l \x00tIPv4\x00G0x80802;0x0\x00d4413\x00o0<...>
               t0\x00PUDP\x00n*:54814\x00TQR=0\x00TQS=0
               <repeating f lines of various forms, fields split by NULL bytes>
               <new 'p' line>
               <repeating f lines>
               ...

               The easiest way to parse it in a single pass is just throw it
               all in a dict then see what's there and do dropout level
               computer science to it.

               This code is needlessly complex because it is common for lsof
               data to be mangled. I'm not sure what causes it but it can be
               seen when manually viewing the files. It's pretty rare, but it
               is important that this function is robust for all cases, all the
               time or data could be silently lost
        """
        raw_socket_count = ip6_socket_count = 0
        pid = cmd = None
        listening = 0
        listen_record = defaultdict(list)
        counter = 0

        for filename, ip_addr in completed:
            counter += 1
            for line in [l.strip() for l in open(filename + '.%s' % (self._cmd), 'r').readlines()]:
                split = line.split('\0')
                # Leave TCP fields for later, they break the convention
                fields = {t[0]: t[1:] for t in split if t and t[0] != 'T'}
                if 'p' in fields:
                    # A `p` line starts a new entry
                    # Example
                    # ['p12345','g12345','R5432','ctelnetd', 'u0', 'Lroot','']
                    pid = int(fields['p'])
                    # These edge cases need to be handled when going over a
                    # large dataset containing output from different operating
                    # systems and versions because anomalies will occur,
                    # including things like 'randomly' split lines. Split lines
                    # make the parser think that a mandatory field is missing.
                    # So for integers, fill in -1, for strings, fill in ''
                    #
                    # This is a best effort at recovering from a corrupt file
                    # as opposed to ignoring its contents
                    #
                    # There is an obvious choice between catching a KeyError
                    # and using the get method. Because the exceptions will
                    # never be raised, it is better to use them rather than
                    # call the get method so many times.. in theory, but I
                    # haven't profiled it. Performance should be fine in
                    # parallel anyway
                    try:
                        pgid = int(fields['g'])
                    except KeyError as err:
                        pgid = -1
                    try:
                        uid = fields['u']
                    except KeyError as err:
                        uid = -1
                    try:
                        cmd = fields['c']
                    except KeyError as err:
                        cmd = ''
                    try:
                        username = fields['L']
                    except KeyError as err:
                        err = err  # PEP8, go away :>
                        username = ''
                else:
                    tcp_fields = {
                        t[0:3]: t[4:] for t in split if t and t[0] == 'T'}
                    if (not tcp_fields) or (
                        'TST' not in tcp_fields) or (
                            tcp_fields['TST'] != 'LISTEN'):
                        continue
                    listening += 1
                    interface = fields['n']
                    if '::' in interface:
                        # Count IPv6 sockets but otherwise ignore them
                        ip6_socket_count += 1
                        continue
                    interface, port = interface.split(':')
                    if port == '*':
                        raw_socket_count += 1
                        continue
                    port = int(port)
                    current = {}
                    current['ip'] = ip_addr
                    current['lsof_port'] = port
                    current['interface'] = interface
                    current['username'] = username
                    current['uid'] = uid
                    current['cmd'] = cmd
                    current['pid'] = pid
                    current['pgid'] = pgid
                    listen_record[(ip_addr, pid)].append(current)
        queue.put(listen_record)
