from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref
    )
from zope.sqlalchemy import ZopeTransactionExtension

pbbDBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
pbbBase = declarative_base()
from pyramid.threadlocal import get_current_registry

settings = get_current_registry().settings
pbb_schema = settings and 'schema.pbb' in settings and settings['schema.pbb'] or 'pbb'