from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
from zope.sqlalchemy import ZopeTransactionExtension
import transaction
    
sipkdDBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
sipkdBase = declarative_base()
