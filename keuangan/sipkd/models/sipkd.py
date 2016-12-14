from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import (
    relationship,
    backref
    )
from sqlalchemy import (Column, Integer, String, SmallInteger, UniqueConstraint, 
                        Date, BigInteger, ForeignKey, func, extract, case, 
                        DateTime, Float)

from ..models import sipkdBase
class SipkdRek4(sipkdBase):
    __tablename__  = 'MATANGD'
    __table_args__ = {'extend_existing':True}   
    mtgkey   = Column(String(10), primary_key=True)
    kdper    = Column(String(30))
    nmper    = Column(String(200))
    mtglevel = Column(String(2))
    kdkhusus = Column(String(1)) 
    type     = Column(String(2)) 
    
    @classmethod
    def get_by_kode(cls, kode):
        if kode[-1:]!='.':
            kode = "%s." % kode
        return SipkdDBSession.query(cls).filter_by(kdper = kode).first()

    @classmethod
    def get_key_by_kode(cls, kode):
        row = cls.get_by_kode(kode)
        return  row and row.mtgkey
        
class SipkdUnit(sipkdBase):
    __tablename__  = 'DAFTUNIT'
    __table_args__ = {'extend_existing':True}   
    unitkey   = Column(String(10), primary_key=True)
    kdlevel   = Column(String(2))
    kdunit    = Column(String(30))
    nmunit    = Column(String(200))
    akrounit  = Column(String(30))
    alamat    = Column(String(200))
    telepon   = Column(String(20))
    type      = Column(String(2))
    @classmethod
    def get_by_kode(cls, kode):
        if kode[-1:]!='.':
            kode = "%s." % kode
        return SipkdDBSession.query(cls).filter_by(kdunit = kode).first()

    @classmethod
    def get_key_by_kode(cls, kode):
        row = cls.get_by_kode(kode)
        return  row and row.unitkey or None
    
################
# TRANSAKSI SKP#
################
class SipkdSkp(sipkdBase):
    __tablename__  = 'SKP'
    __table_args__ = {'extend_existing':True}    
    #units     =  relationship("SipkdUnit",    backref="skp",
    #                        primaryjoin="SipkdUnit.UNITKEY==SipkdSkp.UNITKEY",
    #                        foreign_keys='SipkdSkp.UNITKEY')
    unitkey     = Column(String(10), primary_key=True)
    noskp       = Column(String(50), primary_key=True)
    kdstatus    = Column(String(3))
    keybend     = Column(String(10)) 
    npwpd       = Column(String(10)) 
    idxkode     = Column(Integer)
    tglskp      = Column(DateTime) 
    penyetor    = Column(String(100)) 
    alamat      = Column(String(200)) 
    uraiskp     = Column(String(254)) 
    tgltempo    = Column(DateTime) 
    bunga       = Column(Float) 
    kenaikan    = Column(Float) 
    tglvalid    = Column(DateTime) 
    
class SipkdSkpDet(sipkdBase):
    __tablename__  = 'SKPDET'
    __table_args__ = {'extend_existing':True}    
    #skp     =  relationship("SipkdSkp",    backref="SkpDet",
    #                        primaryjoin="and_(SipkdSkp.UNITKEY==SipkdSkpDet.UNITKEY, "
    #                                    "SipkdSkp.NOSKP==SipkdSkpDet.NOSKP)",
    #                        foreign_keys='SipkdSkpDet.UNITKEY, SipkdSkpDet.NOSKP')
    mtgkey      = Column(String(10), primary_key=True)
    nojetra     = Column(String(2), primary_key=True)
    unitkey     = Column(String(10), primary_key=True)
    noskp       = Column(String(50), primary_key=True)
    nilai       = Column(Float) 
################
# TRANSAKSI TBP#
################
class SipkdTbp(sipkdBase):
    __tablename__  = 'TBP'
    __table_args__ = {'extend_existing':True}    
    unitkey     = Column(String(10), primary_key=True)
    notbp       = Column(String(50), primary_key=True)
    keybend1    = Column(String(10)) 
    kdstatus    = Column(String(3) )
    keybend2    = Column(String(10)) 
    idxkode     = Column(Integer)
    tgltbp      = Column(DateTime) 
    penyetor    = Column(String(100)) 
    alamat      = Column(String(200)) 
    uraitbp     = Column(String(254)) 
    tglvalid    = Column(DateTime) 
  
class SipkdTbpDet(sipkdBase):
    __tablename__  = 'TBPDETD'
    __table_args__ = {'extend_existing':True}    
    mtgkey      = Column(String(10), primary_key=True)
    nojetra     = Column(String(2), primary_key=True)
    unitkey     = Column(String(10), primary_key=True)
    notbp       = Column(String(50), primary_key=True)
    nilai       = Column(Float)
    
class SipkdSkpTbp(sipkdBase):
    __tablename__  = 'SKPTBP'
    __table_args__ = {'extend_existing':True}    
    notbp   = Column(String(50), primary_key=True)
    unitkey = Column(String(10), primary_key=True)
    noskp   = Column(String(50), primary_key=True)
  
class SipkdBkuTbp(sipkdBase):
    __tablename__  = 'BKUTBP'
    __table_args__ = {'extend_existing':True}    
    unitkey     = Column(String(10), primary_key=True)
    nobkuskpd   = Column(String(30), primary_key=True)
    notbp       = Column(String(50))
    idxttd      = Column(String(10))
    tglbkuskpd  = Column(DateTime)
    uraian      = Column(String(254))
    tglvalid    = Column(DateTime)
    keybend     = Column(String(10))
  
class SipkdJurnal(sipkdBase):
    __tablename__  = 'JURNAL'
    __table_args__ = {'extend_existing':True}    
    jbku       = Column(String(2), primary_key=True)
    kdstatus   = Column(String(3), primary_key=True)
    unitkey    = Column(String(10), primary_key=True)
    nobkuskpd  = Column(String(100), primary_key=True)
    nobukti    = Column(String(100), primary_key=True)
    tglbukti   = Column(DateTime)
    uraian     = Column(String(4096))
    kdprgrm    = Column(String(10))
    kdkeg      = Column(String(10))
    keybend    = Column(String(10))
    jns_jurnal = Column(String(2))
    jmatangd   = Column(String(1))
    mtgkeyd    = Column(String(10))
    kdperd     = Column(String(30))
    nmperd     = Column(String(1024))
    nilaid     = Column(Float)
    jmatangk   = Column(String(1))
    mtgkeyk    = Column(String(10))
    kdperk     = Column(String(30))
    nmperk     = Column(String(1024))
    nilaik     = Column(Float)
    jurnal     = Column(Integer)
    tgl_valid  = Column(DateTime)
