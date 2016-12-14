import os
import sys
import transaction
import subprocess
from sqlalchemy import (
    engine_from_config,
    select,
    )
from sqlalchemy.schema import CreateSchema
from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import (
    init_model,
    DBSession,
    Base,
    )
    

#from ..models.ar import *
from ..apbd.models import *
from ..apbd.models.akuntansi import *
    
import initial_data
from tools import mkdir


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

def create_schema(engine, schema):
    sql = select([('schema_name')]).\
          select_from('information_schema.schemata').\
          where("schema_name = '%s'" % schema)
    q = engine.execute(sql)
    if not q.fetchone():
        engine.execute(CreateSchema(schema))

def create_schemas(engine):
    for schema in ['efiling', 'admin', 'aset', 'eis', 'gaji', 'apbd']:
        create_schema(engine, schema)

def read_file(filename):
    f = open(filename)
    s = f.read()
    f.close()
    return s

def main(argv=sys.argv):
    def alembic_run(ini_file, url):
        s = read_file(ini_file)
        s = s.replace('{{db_url}}', url)
        f = open('alembic.ini', 'w')
        f.write(s)
        f.close()
        subprocess.call(command)   
        os.remove('alembic.ini')

    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    # Create Ziggurat tables
    bin_path = os.path.split(sys.executable)[0]
    alembic_bin = os.path.join(bin_path, 'alembic') 
    command = (alembic_bin, 'upgrade', 'head')    
    
    if 'pbb.url' in settings and settings['pbb.url']:
        from ..pbb.models import pbbDBSession, pbbBase
        #alembic_run('alembic.ini.tpl', settings['pbb.url'])
        #alembic_run('alembic_upgrade.ini.tpl', settings['pbb.url'])
        
        engine_pbb = engine_from_config(settings, 'pbb.')
        pbbDBSession.configure(bind=engine_pbb)
        from ..pbb.models.tap import SaldoAwal
        pbbBase.metadata.create_all(engine_pbb)
        transaction.commit()
        print '****PBB CREATED****'
        #sys.exit()

    if 'sipkd.url' in settings and settings['sipkd.url']:
        from ..sipkd.models import sipkdDBSession, sipkdBase
        from ..sipkd.models.sipkd import SipkdRek4
        
        engine_sipkd = engine_from_config(settings, 'sipkd.')
        sipkdDBSession.configure(bind=engine_sipkd)
        sipkdBase.metadata.create_all(engine_sipkd)
        transaction.commit()
        print '****SIPKD CREATED****'
        #sys.exit()
        
    if 'bphtb.url' in settings and settings['bphtb.url']:
        from ..bphtb.models import bphtbDBSession, bphtbBase
        #alembic_run('alembic.ini.tpl', settings['pbb.url'])
        #alembic_run('alembic_upgrade.ini.tpl', settings['pbb.url'])
        
        engine_bphtb = engine_from_config(settings, 'bphtb.')
        bphtbDBSession.configure(bind=engine_bphtb)
        from ..bphtb.models.transaksi import SaldoAwal
        bphtbBase.metadata.create_all(engine_bphtb)
        transaction.commit()
        print '****BPHTB CREATED****'
        #sys.exit()

    alembic_run('alembic.ini.tpl', settings['sqlalchemy.url'])
    alembic_run('alembic_upgrade.ini.tpl', settings['sqlalchemy.url'])
    # Insert data
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    init_model()
    #create_schemas(engine)
    Base.metadata.create_all(engine)
    initial_data.insert()
    transaction.commit()
