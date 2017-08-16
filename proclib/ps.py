from common import ProcToolWorker


class PS(ProcToolWorker):
    """
        A parallellized ps output parser

        Input:
            Path to ps results files

        Output:
            A dictionary with key (ip, pid) containing process information for
            all listening sockets. This can be merged with lsof output for more
            complete info.

        Notes:
            By default, it will paralellize into CPU count + 1 because this can
            be very slow depending on how many files you have to process.

            The system CPU count is acquired via POSIX sysconf()
    """
    def __init__(self, results_path, cmd, extension='.ret.complete'):
        super(self.__class__, self).__init__(
            results_path,
            cmd,
            extension=extension)
        print('Initialized PS')

    def load(self, completed, queue):
        """
        Meant to be called as a Process, it parses a file containing output
        from ps and returns a dictionary via a queue to the parent.

        Expects input of the format that is produced by:
            # ps -e -o pid= -o user= -o comm= -o args=

        There should never be an exception in parsing this data, it is very
        simple field based data and the only place for additional fields, i.e.
        spaces, is at the end, which is taken into consideration when assigning
        argv

        Input:

            completed: list of filenames to iterate over and process
            queue: a read/write queue back to the function that invoked this
            via Process()

        Output:

            Results: dict of all parsed results with (ip,pid) tuple as the key.
                     This is returned via the queue. The function itself
                     returns None
        """
        results = {}
        # This is a decision that could potentially result in missing data
        # It is arguable whether this is the "correct" thing to do but on some
        # platforms rows of these types of processes cannot be parsed reliably
        # Probably less of an issue when using only Linux
        known_nonconformant = ('<defunct>', '<exiting>', '<idle>')
        for filename, ip in completed:
            for line in [l.strip() for l in open(filename + '.%s' % (
                    self._cmd), 'r').readlines()]:
                split = line.split()
                if len(split) < 3:
                    if split[1] in known_nonconformant:
                        continue
                    else:
                        print split
                        raise Exception('Bad ps line !!')

                pid = int(split[0])
                # User is an ascii integer if username is too long
                user = split[1]
                cmd = split[2]  # argv[0]
                # Process has no arguments
                if len(split) == 3:
                    argv_zero = cmd
                    argv = ['']
                # Process has arguments
                else:
                    argv_zero = split[3]
                    argv = split[3:]
                record = {}
                record['pid'] = pid
                record['user'] = user
                record['ps_cmd'] = cmd
                record['ps_argv'] = ' '.join(argv)
                record['ip'] = ip
                record['ps_argv_zero'] = argv_zero
                results[(ip, pid)] = record
        # Push back to parent process over the Queue object
        queue.put(results)
        return None
