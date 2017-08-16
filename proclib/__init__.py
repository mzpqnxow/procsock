from lsof import LSOF
from ps import PS


def join_network_socket_procdata(lsof_data, ps_data):
    """
        Walk through all lsof entries, which are keyed by (IP, PID) and
        contain a list of listening sockets as their value

        For each, augment with the matching ps data into the `joined`
        dictionary, which is a dictionary keys on (IP, PORT)

        Return the joined dictionary
    """

    joined = {}
    for (ip, pid), services in lsof_data.iteritems():
        for service in services:
            port = service['lsof_port']
            ps_record = ps_data[(ip, pid)]
            service['ps_argv_zero'] = ps_record['ps_argv_zero']
            service['ps_argv'] = ps_record['ps_argv']
            service['ps_username'] = ps_record['user']
            joined[(ip, port)] = service
    return joined


__all__ = [LSOF, PS]
