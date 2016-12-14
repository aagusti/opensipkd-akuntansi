from ...models import Base, DefaultModel, DBSession
from ..models import UraianModel
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    SmallInteger,
    Text,
    DateTime,
    String,
    ForeignKey,
    text,
    UniqueConstraint,
    )
    
from sqlalchemy.orm import (
    relationship,
    backref
    )

ARGS =  {'extend_existing':True, 
         #'schema' : 'admin',
        }    
class Rekening(UraianModel, Base):
    __tablename__ = 'rekenings'
    __table_args__= (UniqueConstraint('kode', 'tahun', name='rekening_uq'),
                     ARGS)
                      
    tahun     = Column(Integer)
    nama      = Column(String(256))
    level_id  = Column(SmallInteger, default=1)
    parent_id = Column(BigInteger,   ForeignKey('rekenings.id'))
    disabled  = Column(SmallInteger, default=0)
    defsign   = Column(SmallInteger, default=1)
    children  = relationship("Rekening", backref=backref('parent', remote_side='Rekening.id'))
    
    @classmethod
    def get_next_level(cls,id):
        return cls.query_id(id).first().level_id+1
       
class Sap(UraianModel, Base):
    __tablename__ = 'saps'
    __table_args__= (UniqueConstraint('kode', 'tahun', name='sap_uq'),
                     ARGS)
                      
    tahun     = Column(Integer)
    nama      = Column(String(256))
    level_id  = Column(SmallInteger, default=1)
    parent_id = Column(BigInteger,   ForeignKey('saps.id'))
    disabled  = Column(SmallInteger, default=0)
    defsign   = Column(SmallInteger, default=1)
    children  = relationship("Sap", backref=backref('parent', remote_side='Sap.id'))
    
    @classmethod
    def get_next_level(cls,id):
        return cls.query_id(id).first().level_id+1

class RekeningSap(DefaultModel, Base):
    __tablename__    = 'rekenings_saps'
    __table_args__   = ARGS
                     
    rekening_id      = Column(Integer, ForeignKey("rekenings.id"))        
    db_lo_sap_id     = Column(Integer, nullable=True)
    kr_lo_sap_id     = Column(Integer, nullable=True)
    db_lra_sap_id    = Column(Integer, nullable=True)
    kr_lra_sap_id    = Column(Integer, nullable=True)
    neraca_sap_id    = Column(Integer, nullable=True)
    pph_id           = Column(String(64))
    
    rekenings   = relationship("Rekening", backref="rekenings_saps")
        
class DasarHukum(DefaultModel, Base):
    __tablename__  = 'dasar_hukums'
    __table_args__ = ARGS
    
    rekenings   = relationship("Rekening", backref="dasar_hukums")
    rekening_id = Column(Integer, ForeignKey("rekenings.id"))   
    no_urut     = Column(Integer)     
    nama        = Column(String(256))
    
# class SaldoAwal(pbbBase, CommonModel):
    # __tablename__  = 'saldo_awal'
    # __table_args__ = ARGS
    # tahun       = Columns(String(4))
    # tahun_tetap = Columns(String(4))
    # rekening_id = Column(Integer, ForeignKey("rekenings.id"))   
    # uraian      = Columns(String(500))
    # nilai       = Columns(BigInteger)
    # rekenings   = relationship("Rekening", backref="rekenings")
    
class Jurnal(UraianModel, Base):
    __tablename__   = 'jurnals'
    __table_args__  = ARGS
                    
    units           = relationship("Unit",  backref=backref("jurnals")) 
    unit_id         = Column(Integer,       ForeignKey("units.id"), nullable=False)  
    tahun_id        = Column(Integer)
    kode            = Column(String(32),    nullable=False)    
    nama            = Column(String(255),   nullable=False)
    jv_type         = Column(SmallInteger,  nullable=False, default=0)
    tanggal         = Column(DateTime) 
    tgl_transaksi   = Column(DateTime)
    periode         = Column(Integer,       nullable=False)
    source          = Column(String(10),    nullable=False)
    source_no       = Column(String(30),    nullable=False)
    #source_id       = Column(String(30),    nullable=False)
    tgl_source      = Column(DateTime)           
    posted          = Column(SmallInteger,  nullable=False)
    posted_uid      = Column(Integer) 
    posted_date     = Column(DateTime) 
    notes           = Column(String(225),   nullable=False)
    is_skpd         = Column(SmallInteger,  nullable=False)
    no_urut         = Column(BigInteger,    nullable=True)
    disabled        = Column(SmallInteger,  nullable=False, default=0)

    @classmethod
    def max_no_urut(cls, tahun, unit_id):
        return DBSession.query(func.max(cls.no_urut).label('no_urut'))\
                .filter(cls.tahun_id==tahun,
                        cls.unit_id==unit_id
                ).scalar() or 0
                
    @classmethod
    def get_norut(cls, tahun, unit_id):
        return DBSession.query(func.count(cls.id).label('no_urut'))\
               .filter(cls.tahun_id==tahun,
                       cls.unit_id ==unit_id
               ).scalar() or 0
               
    @classmethod
    def get_tipe(cls, jv_type):
        return DBSession.query(case([(cls.jv_type==1,"JT"),(cls.jv_type==2,"JK"),
                          (cls.jv_type==3,"JU"),(cls.jv_type==4,"KR"),
                          (cls.jv_type==5,"CL"),(cls.jv_type==6,"LO")], else_="").label('jv_type'))\
                .filter(cls.jv_type==jv_type
                ).group_by(cls.jv_type
                ).scalar() or 0
                
class JurnalItem(DefaultModel, Base):
    __tablename__   ='jurnal_items'
    __table_args__  = ARGS

    jurnals         = relationship("Jurnal", backref="jurnal_items")
    jurnal_id       = Column(BigInteger, ForeignKey("jurnals.id"), nullable=False)
    kegiatan_sub_id = Column(BigInteger, default=0, nullable=True) 
    rekening_id     = Column(BigInteger, default=0, nullable=True)
    sap_id          = Column(BigInteger, default=0, nullable=True)
    amount          = Column(BigInteger, default=0) 
    notes           = Column(String(225),nullable=True)
