# -*- coding: utf-8 -*-
""" proclib, a library for joining lsof and ps data into one record

Miscellaneous functions and imports for proclib

This library is used to join lsof and ps data gathered on a host by procksocksh
into one lookup table. It works in parallel to speed up cases where thousands of
hosts are surveyed

Copyright (C) 2017 copyright /at/ mzpqnxow.com under the MIT license
Please see COPYRIGHT for terms
"""
from __future__ import print_function
from proclib.lsof import LSOF
from proclib.ps import PS


def join_network_socket_procdata(lsof_data, ps_data):
    """
    Walk through all lsof entries, which are keyed by (IP, PID) and
    contain a list of listening sockets as their value

    For each, augment with the matching ps data into the `joined`
    dictionary, which is a dictionary keys on (IP, PORT)

    Return the joined dictionary
    """

    joined = {}
    for (ip_addr, pid), services in lsof_data.iteritems():
        for service in services:
            port = service['lsof_port']
            ps_record = ps_data[(ip_addr, pid)]
            service['ps_argv_zero'] = ps_record['ps_argv_zero']
            service['ps_argv'] = ps_record['ps_argv']
            service['ps_username'] = ps_record['user']
            joined[(ip_addr, port)] = service
    return joined


__all__ = ['LSOF', 'PS']
