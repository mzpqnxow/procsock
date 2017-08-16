from multiprocessing import Process, Queue
from os import sysconf
import re
import os
import sys
import time
from glob import glob


class ProcToolWorker(object):
    IP_DATE_RE_COMPILED = re.compile(
        r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\.(\d{12})')

    def __init__(self, results_path, cmd, extension='.ret.complete'):
        self._results_path = results_path
        self._debug = None
        self._cmd = cmd
        self._extension = extension

    def _enumerate_acquisitions(self, directory, suffix):
        records = []
        glob_pattern = "*%s" % suffix
        full_glob = os.sep.join((directory, glob_pattern))
        for filename in glob(full_glob):
            match = self.IP_DATE_RE_COMPILED.search(filename)
            if not match:
                raw_input("Malformed file '%s' - continue?" % filename)
            ip = match.group(1)
            records.append((self._basename(filename), ip))
        return records

    def _basename(self, name, depth=2):
        return '.'.join(name.split('.')[0:-2])

    def _cpu_chunk(self, items, cpu_count):
        worker_chunks = []
        remainder = len(items) % cpu_count
        chunk_size = len(items) / cpu_count
        for cpu in xrange(0, cpu_count - 1):
            worker_chunks.append(
                items[cpu * chunk_size:cpu * chunk_size + chunk_size])
        worker_chunks.append(items[-chunk_size - remainder:])
        return worker_chunks

    def get_time(self):
        return self._run_time

    def go_paralell(self, force_process_count=None):
        """
            Given n logical CPUs, chunk up the records into n equal sized
            batches, create n Process and Queue objects, kick off each Process
            and merge ps and lsof records in a loop. Pass back the results
            through through the Queues. Very basic fork() style
            multiprocessing.

            This could be done as Threads but given it is CPU bound, the GIL
            will almost certainly slow things down. Because batches are handled
            by each Process, the overhead of creating the Process becomes small
            when compared with the amount of work it performs, so there is no
            real performance penalty
        """
        start_time = int(time.time())
        print(
            'Stage 1 - enumerate and parse all process records from all hosts')
        completed = self._enumerate_acquisitions(
            self._results_path, self._extension)

        if not force_process_count:
            cpu_count = sysconf('SC_NPROCESSORS_ONLN')
        else:
            assert type(force_process_count) == int
            cpu_count = force_process_count

        completed_sets = self._cpu_chunk(completed, cpu_count)
        print('- %d total IP process listings discovered on filesystem' % (
            len(completed)))
        print('- sysconf(SC_NPROCESSORS_ONLN) == %d' % cpu_count)
        print
        print('Work will be split across %d %s' % (
            cpu_count,
            'logical processors' if not force_process_count else 'processes'))
        print
        processes = []
        print('Starting processes...')
        for i in completed_sets:
            queue = Queue()
            process = Process(target=self.load, args=(i, queue))
            processes.append((process, queue))
        for cpu, (p, q) in enumerate(processes):
            print('(%s) start %s #%d' % (
                self._cmd,
                'CPU' if not force_process_count else 'process', cpu))
            p.start()
        print
        results = {}
        for cpu, (p, q) in enumerate(processes):
            sys.stdout.write('-- waiting for result from %s#%.2d ... ' % (
                'CPU' if not force_process_count else 'process', cpu))
            sys.stdout.flush()
            result = q.get()
            sys.stdout.write("done\n")
            results.update(result)
            p.join()
            print('\t[*] %s#%.2d complete (%d processess discovered)' % (
                'CPU' if not force_process_count else 'process',
                cpu,
                len(result)))
        print
        end_time = int(time.time())
        self._run_time = end_time - start_time
        return results
