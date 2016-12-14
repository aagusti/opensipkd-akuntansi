import os
import sys
import re
from urlparse import urlsplit
from commands import getoutput


def run(s):
    print(s)
    if os.system(s) != 0:
        sys.exit()

def url2filename(url):
    t = urlsplit(url)
    fullpath = t.path
    t = os.path.split(t.path)
    return t[-1]

def debfile2name(filename):
    filename = os.path.split(filename)[-1]
    t = filename.split('_')
    return t[0]

def wget_install(url):
    filename = url2filename(url)
    if not os.path.exists(filename):
        run('wget ' + url)
    dpkg_install(filename)

def dpkg_install(filename):
    name = debfile2name(filename)
    if is_installed(name):
        return True
    run('dpkg -i ' + filename)

def apt_get_install(name):
    if is_installed(name):
        return True
    command = 'apt-get -y install ' + name
    run(command)

def is_installed(name):
    return getoutput('dpkg -l | grep %s | grep ^ii' % name)
    regex = re.compile(r'^Status: install ok installed')
    for line in s.splitlines():
        print([line])
        match = regex.search(line)
        if match:
            return True

def error(s):
    print(s)
    sys.exit()
    

download_list = [
    'http://vpn.opensipkd.com/oracle/client/oracle-instantclient11.2-basiclite_11.2.0.3.0-2_amd64.deb',
    'http://vpn.opensipkd.com/oracle/client/oracle-instantclient11.2-devel_11.2.0.3.0-2_amd64.deb',
    ]
apt_get_list = ['build-essential', 'python-dev', 'python-pip', 'libaio1']

try:
    import cx_Oracle
    error('Modul cx_Oracle sudah terpasang.')
except ImportError:
    pass

for name in apt_get_list:
    apt_get_install(name)

for url in download_list:
    wget_install(url)

oracle_home = '/usr/lib/oracle/11.2/client64/lib'
include_orig_dir = '/usr/include/oracle/11.2/client64'
sdk_dir = '/'.join([oracle_home, 'sdk'])
include_dir = '/'.join([sdk_dir, 'include'])
if not os.path.exists(sdk_dir):
    os.mkdir(sdk_dir)
if not os.path.exists(include_dir):
    os.symlink(include_orig_dir, include_dir)
    
shared_lib_conf = '/etc/ld.so.conf.d/oracle.conf'
if not os.path.exists(shared_lib_conf):
    f = open(shared_lib_conf, 'w')
    f.write(oracle_home)
    f.close()
    run('ldconfig')

run('export ORACLE_HOME="%s"; pip install cx-oracle' % oracle_home)
    
try:
    import cx_Oracle
    print('Modul cx_Oracle berhasil dipasang.')
except ImportError, err:
    print(err)
