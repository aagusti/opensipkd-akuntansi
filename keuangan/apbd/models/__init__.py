from ...models import Base, DefaultModel, DBSession
from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    func,
    String,
    ForeignKey,
    SmallInteger
    )
from datetime import datetime
from sqlalchemy.orm import (
    relationship,
    backref
    )
    
class KodeModel(DefaultModel):
    kode = Column(String(32))
    status = Column(SmallInteger, nullable=False, default=0, 
                server_default='0')
    created  = Column(DateTime, nullable=False, default=datetime.now,
                server_default='now()')
    updated  = Column(DateTime)
    create_uid  = Column(Integer, nullable=False, default=1,
                    server_default='1')
    update_uid  = Column(Integer)
    
    @classmethod
    def get_by_kode(cls,kode):
        return cls.query().filter_by(kode=kode).first()
        
    @classmethod
    def count(cls):
        return DBSession.query(func.count('*')).scalar()
    
    @classmethod
    def get_active(cls):
        return DBSession.query(cls).filter_by(status=1).all()
    
    
    
class UraianModel(KodeModel):
    uraian = Column(String(255))
    @classmethod
    def get_by_uraian(uraian):
        return cls.query().filter_by(uraian=uraian).first()
        
    @classmethod
    def get_uraian(uraian):
        return cls.query().filter_by(uraian=uraian)


# class App(Base, NamaModel):
    # __tablename__  = 'apps'
    # __table_args__ = {'extend_existing':True, 
                      # 'schema' : 'admin',}
    # tahun = Column(Integer)
    
    # @classmethod
    # def count_active(cls):
        # return DBSession.query(func.count(cls.id)).filter(cls.disabled==0).scalar()
    # @classmethod
    # def active_url(cls):
        # return DBSession.query(cls.kode).filter(cls.disabled==0).first().kode
        
ARGS = {'extend_existing':True}
        
# class Urusan(Base, UraianModel):
    # __tablename__  = 'urusans'
    # __table_args__ = ARGS

class Unit(Base, UraianModel):
    __tablename__  = 'units'
    __table_args__ = ARGS
                       
    #urusan_id = Column(Integer, ForeignKey('admin.urusans.id'))
    tipe      = Column(String(32))
    alamat    = Column(String(255))
    singkat   = Column(String(32))
    level_id  = Column(SmallInteger)
    header_id = Column(SmallInteger)
    #urusan_id = Column(Integer, ForeignKey('urusans.id'))
    #urusans   = relationship("Urusan", backref="units")

# class UserUnit(Base, CommonModel):
    # __tablename__  = 'user_units'
    # __table_args__ = {'extend_existing':True, 
                      # 'schema' : 'admin',}
     
    # units    = relationship("Unit", backref="users")
    # users    = relationship("User", backref="units")                  
    # user_id  = Column(Integer, ForeignKey('users.id'),       primary_key=True)
    # unit_id  = Column(Integer, ForeignKey('admin.units.id'), primary_key=True)
    # sub_unit = Column(SmallInteger, nullable=False)
    
    # @classmethod
    # def query_user_id(cls, user_id):
        # return DBSession.query(cls).filter_by(user_id = user_id)

    # @classmethod
    # def ids(cls, user_id):
        # r = ()
        # units = DBSession.query(cls.unit_id,cls.sub_unit, Unit.kode
                     # ).join(Unit).filter(cls.unit_id==Unit.id,
                            # cls.user_id==user_id).all() 
        # for unit in units:
            # if unit.sub_unit:
                # rows = DBSession.query(Unit.id).filter(Unit.kode.ilike('%s%%' % unit.kode)).all()
            # else:
                # rows = DBSession.query(Unit.id).filter(Unit.kode==unit.kode).all()
            # for i in range(len(rows)):
                # print '***', rows[i]
                # r = r + (rows[i])
        # return r
        
    # @classmethod
    # def unit_granted(cls, user_id, unit_id):
        
        # print 'A*******',  user_id, unit_id
        # units = DBSession.query(cls.unit_id,cls.sub_unit, Unit.kode
                     # ).join(Unit).filter(cls.unit_id==Unit.id,
                            # cls.user_id==user_id).all() 
        # for unit in units:
            # if unit.sub_unit:
                # rows = DBSession.query(Unit.id).filter(Unit.kode.ilike('%s%%' % unit.kode)).all()
            # else:
                # rows = DBSession.query(Unit.id).filter(Unit.kode==unit.kode).all()
            # for i in range(len(rows)):
                # if int(rows[i][0])  == int(unit_id):
                    # return True
        # return False
        
    # @classmethod
    # def get_filtered(cls, request):
        # filter = "'%s' LIKE admin.units.kode||'%%'" % request.session['unit_kd']
        # q1 = DBSession.query(Unit.kode, UserUnit.sub_unit).join(UserUnit).\
                       # filter(UserUnit.user_id==request.user.id,
                              # UserUnit.unit_id==Unit.id,
                              # text(filter))
        # return q1.first()
       