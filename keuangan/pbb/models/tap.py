import sys
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    String,
    SmallInteger,
    types,
    func,
    ForeignKeyConstraint,
    literal_column,
    and_
    )
from sqlalchemy.orm import aliased

from sqlalchemy.orm.exc import NoResultFound

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref,
    #primary_join
    )
import re
from ...tools import as_timezone, FixLength

from ...models import CommonModel
from ..models import pbbBase, pbbDBSession, pbb_schema

#from ref import Kelurahan, Kecamatan, Dati2, KELURAHAN, KECAMATAN
    
PBB_ARGS = {'extend_existing':True,  
        'autoload':True,
        'schema': pbb_schema}    

class SaldoAwal(pbbBase, CommonModel):
    __tablename__  = 'saldo_awal'
    __table_args__ = {'extend_existing':True, 
                      'schema': pbb_schema}    

    id          = Column(BigInteger, primary_key=True)
    tahun       = Column(String(4))
    tahun_tetap = Column(String(4))
    uraian      = Column(String(200))
    nilai       = Column(BigInteger)
    posted      = Column(Integer)
    created      = Column(DateTime)
    create_uid   = Column(Integer)
    updated      = Column(DateTime)
    update_uid   = Column(Integer)
                      
class Sppt(pbbBase, CommonModel):
    __tablename__  = 'sppt'
    __table_args__ = PBB_ARGS
    kd_propinsi = Column(String(2), primary_key=True)
    kd_dati2 = Column(String(2), primary_key=True)
    kd_kecamatan = Column(String(3), primary_key=True)
    kd_kelurahan = Column(String(3), primary_key=True)
    kd_blok = Column(String(3), primary_key=True)
    no_urut = Column(String(4), primary_key=True)
    kd_jns_op = Column(String(1), primary_key=True)
    thn_pajak_sppt = Column(String(4), primary_key=True)
    
class SpptAkrual(pbbBase, CommonModel):
    __tablename__  = 'sppt_akrual'
    __table_args__ = PBB_ARGS
    kd_propinsi = Column(String(2), primary_key=True)
    kd_dati2 = Column(String(2), primary_key=True)
    kd_kecamatan = Column(String(3), primary_key=True)
    kd_kelurahan = Column(String(3), primary_key=True)
    kd_blok = Column(String(3), primary_key=True)
    no_urut = Column(String(4), primary_key=True)
    kd_jns_op = Column(String(1), primary_key=True)
    thn_pajak_sppt = Column(String(4), primary_key=True)
    siklus_sppt = Column(Integer, primary_key=True)
    
class SpptRekap(pbbBase, CommonModel):
    __tablename__  = 'sppt_rekap'
    __table_args__ = PBB_ARGS 
    id          = Column(BigInteger, primary_key=True)
    tanggal     = Column(DateTime)
    kode      = Column(String(30))
    uraian      = Column(String(200))
    pokok       = Column(BigInteger)
    posted      = Column(Integer)
    created      = Column(DateTime)
    create_uid   = Column(Integer)
    updated      = Column(DateTime)
    update_uid   = Column(Integer)
    
    
class PembayaranSppt(pbbBase, CommonModel):
    __tablename__  = 'pembayaran_sppt'
    __table_args__ = (
                      # ForeignKeyConstraint(['kd_propinsi','kd_dati2','kd_kecamatan','kd_kelurahan',
                              # 'kd_blok', 'no_urut','kd_jns_op', 'thn_pajak_sppt'], 
                              # ['sppt.kd_propinsi', 'sppt.kd_dati2',
                               # 'sppt.kd_kecamatan','sppt.kd_kelurahan',
                               # 'sppt.kd_blok', 'sppt.no_urut',
                               # 'sppt.kd_jns_op','sppt.thn_pajak_sppt']),
                      PBB_ARGS)
    kd_propinsi = Column(String(2), primary_key=True)
    kd_dati2 = Column(String(2), primary_key=True)
    kd_kecamatan = Column(String(3), primary_key=True)
    kd_kelurahan = Column(String(3), primary_key=True)
    kd_blok = Column(String(3), primary_key=True)
    no_urut = Column(String(4), primary_key=True)
    kd_jns_op = Column(String(1), primary_key=True)
    thn_pajak_sppt = Column(String(4), primary_key=True)
    pembayaran_sppt_ke = Column(Integer, primary_key=True)

class PembayaranRekap(pbbBase, CommonModel):
    __tablename__  = 'pembayaran_sppt_rekap'
    __table_args__ = PBB_ARGS  

    id          = Column(BigInteger, primary_key=True)
    tanggal     = Column(DateTime)
    kode      = Column(String(30))
    uraian      = Column(String(200))
    denda       = Column(BigInteger)
    bayar       = Column(BigInteger)
    posted      = Column(Integer)
    created      = Column(DateTime)
    create_uid   = Column(Integer)
    updated      = Column(DateTime)
    update_uid   = Column(Integer)
    
    