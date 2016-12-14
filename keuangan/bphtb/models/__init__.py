from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref
    )
from zope.sqlalchemy import ZopeTransactionExtension

bphtbDBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
bphtbBase = declarative_base()
from ...tools import get_settings

settings = get_settings()
bphtb_schema = settings and 'schema.bphtb' in settings and settings['schema.bphtb'] or None
bphtb_schema = 'bphtb'