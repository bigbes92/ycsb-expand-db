#!/usr/bin/env python

from db import DB
from db import timet, chroot_, get_time

import shlex
import shutil
import os
import fileinput
import socket

from time import sleep, time
from subprocess import PIPE, STDOUT, Popen
from copy import deepcopy
from pprint import pprint

class TokuMX(DB):
    _exe = "mongod"
    _cli = "mongo"
    _cnf = "mongodb.conf"
    _log = "mongodb.log"

    st_args = {
            'dbpath'            : './temp',
            'logpath'           : './mongodb.log',
            'diaglog'           : '3',
            'logappend'         : '',
            'nojournal'         : '',
            'noauth'            : '',
            'nohttpinterface'   : '',
            'noprealloc'        : ''
            }

    def __init__(self, _dir):
        self._dir = _dir
        self._run = None
        self.port = '27017'
        self._args = deepcopy(self.st_args)
        self.add_arg(('port', self.port))
        if not (os.path.exists(self._dir+'/'+self._exe) and
                os.path.exists(self._dir+'/'+self._cli)):
            raise Exception('No such file or directory in DB: ' + self._dir)

    def set_port(self, port):
        self.port = port
        self.add_arg(('port', self.port))

    def __del__(self):
        self.stop()

    @chroot_
    def cleanup(self):
        try:
            shutil.rmtree('temp')
        except OSError:
            pass
        try:
            os.mkdir('temp')
        except OSError:
            pass

    def init(self):
        self.cleanup()
        print ">>Cleanup TokuMX"

    def flush_db(self):
        if self._run:
            print "<<Start TokuMX, Please"
            return -1
        Popen(shlex.split(self._dir+self._cli+"localhost"
            +self.port+"/ycsb --eval \"db.dropDatabase()\"")).wait()
        print ">>Flushing TokuMX"

    def load_snapshot(self):
        if self._run:
            print "<<Stop TokuMX, Please"
            return -1
        return get_time(self)

    def add_arg(self, args):
        self._args[str(args[0])] = str(args[1])

    # Cause TokuMX(MongoDB) use Memory Maped files - not implementing
    def save_snapshot(self):
        print "<<Not Yet Implemented"
        return 0

    @chroot_
    def start(self, delay = None):

        if delay == None:
            delay = True
        def args_to_str(self):
            return ''.join(map(lambda x: ' --'+x+' '+self._args[x], self._args))
        os.environ["LD_LIBRARY_PATH"] = "."
        if self._run:
            print "<<TokuMX already started."
            return -1
        print ">>Starting TokuMX"
        args = shlex.split("./"+self._exe+" -f mongodb.conf")
        self._run = Popen(args)
        if delay:
            print get_time(self)
        print ">>TokuMX PID:", self._run.pid

    def stop(self):
        if not self._run:
            print ">>TokuMX already stopped"
            return -1
        self._run.send_signal(2)
        self._run.wait()
        self._run = None
        print ">>Stopping TokuMX"
