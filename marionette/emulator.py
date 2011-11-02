import datetime
import os
import re
import subprocess
import time


class Emulator(object):

    deviceRe = re.compile(r"^emulator-(\d+)(\s*)(.*)$")

    def __init__(self, homedir=None):
        self.port = None
        self.proc = None

        self.homedir = homedir
        if self.homedir is None:
            self.homedir = os.getenv('B2G_HOME')
        if self.homedir is None:
            raise Exception('Must define B2G_HOME or pass the homedir parameter')

        self.adb = os.path.join(self.homedir,
                                'glue/gonk/out/host/linux-x86/bin/adb')

        self.binary = os.path.join(self.homedir,
                                   'glue/gonk/out/host/linux-x86/bin/emulator')
        self._check_file(self.binary)

        self.kernelImg = os.path.join(self.homedir,
                                      'boot/kernel-android-qemu/arch/arm/boot/zImage')
        self._check_file(self.kernelImg)

        self.sysDir = os.path.join(self.homedir, 
                                   'glue/gonk/out/target/product/generic/')
        self._check_file(self.sysDir)

        self.dataImg = os.path.join(self.sysDir, 'userdata.img')
        self._check_file(self.dataImg)

    def _check_file(self, filePath):
        if not os.access(filePath, os.F_OK):
            raise Exception(('File not found: %s; did you pass the B2G home '
                             'directory as the homedir parameter, or set '
                             'B2G_HOME correctly?') % filePath)

    @property
    def args(self):
        return [
                    self.binary,
                    '-kernel', self.kernelImg,
                    '-sysdir', self.sysDir,
                    '-data', self.dataImg,
                    '-memory', '512',
                    '-verbose',
                    '-qemu', '-cpu', 'cortex-a8'
               ]

    @property
    def is_running(self):
        return self.proc is not None and self.proc.poll() is None

    def _run_adb(self, args):
        args.insert(0, self.adb)
        adb = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retcode = adb.wait()
        if retcode:
            raise Exception('adb terminated with exit code %d: %s' 
                            % (retcode, adb.stdout.read()))
        return adb.stdout.read()

    def close(self):
        if self.is_running:
            self.proc.terminate()
            self.proc.wait()
        if self.proc:
            retcode = self.proc.poll()
            self.proc = None
            return retcode

    def _get_adb_devices(self):
        offline = set()
        online = set()
        output = self._run_adb(['devices'])
        for line in output.split('\n'):
            m = self.deviceRe.match(line)
            if m:
                if m.group(3) == 'offline':
                    offline.add(m.group(1))
                else:
                    online.add(m.group(1))
        return (online, offline)
    
    def start(self):
        self._run_adb(['start-server'])

        original_online, original_offline = self._get_adb_devices()

        self.proc = subprocess.Popen(self.args,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)

        online, offline = self._get_adb_devices()
        now = datetime.datetime.now()
        while online - original_online == set([]):
            time.sleep(1)
            if datetime.datetime.now() - now > datetime.timedelta(seconds=60):
                raise Exception('timed out waiting for emulator to start')
            online, offline = self._get_adb_devices()
        self.port = int(list(online - original_online)[0])

    def setup_port_forwarding(self, remote_port):
        """ Setup TCP port forwarding to the specified port on the device,
            using any availble local port, and return the local port.
        """

        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("",0))
        local_port = s.getsockname()[1]
        s.close()

        output = self._run_adb(['-s', 'emulator-%d' % self.port, 
                                'forward',
                                'tcp:%d' % local_port,
                                'tcp:%d' % remote_port])
        print output

        return local_port

