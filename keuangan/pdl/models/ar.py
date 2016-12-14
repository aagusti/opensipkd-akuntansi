from datetime import datetime
from sqlalchemy import (Column, Integer, String, SmallInteger, UniqueConstraint, 
                        Date, BigInteger, ForeignKey, func, extract, case, DateTime)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship, backref
    )
from datetime import datetime
from zope.sqlalchemy import ZopeTransactionExtension
import transaction
from ..tools import as_timezone
from ..models import (DBSession, DefaultModel,Base,)
from ..models import (NamaModel)
#from ..models.pemda import (Unit)
#from ..models.ak import(Rekening)
#from ..models.apbd_anggaran import (KegiatanSub)
schematbl = 'public'

class ARInvoiceTrans(DefaultModel, Base):
    __tablename__  = 'ar_invoice_trans'
    __table_args__ = {'extend_existing':True, 'schema' : schematbl,}
    tahun           = Column(Integer, nullable=False)
    unit_kd         = Column(String,  nullable=False) 
    unit_nm         = Column(String(128))
    kode            = Column(String(50))
    nama            = Column(String(255))
    alamat          = Column(String(255))
    uraian          = Column(String(255))
    tgl_tetap       = Column(Date)    
    tgl_validasi    = Column(Date)
    rekening_kd     = Column(String(16))
    rekening_nm     = Column(String(128))
    pokok           = Column(BigInteger)
    denda           = Column(BigInteger)
    bunga           = Column(BigInteger)
    nilai           = Column(BigInteger, nullable=False)
    #status          = Column(SmallInteger, nullable=False, default=0)
    sumber_id       = Column(SmallInteger, default=1)#1, 2, 3, 4
    sumber_nm       = Column(String(16))#1, 2, 3, 4
    posted          = Column(SmallInteger, nullable=False, default=0)
    ref_kode         = Column(String(32), unique=True)
    ref_nama         = Column(String(64))
    kecamatan_kd     = Column(String(32))
    kecamatan_nm     = Column(String(64))
    kelurahan_kd     = Column(String(32))
    kelurahan_nm     = Column(String(64))
    tahun            = Column(Integer)
    bulan            = Column(Integer)
    minggu           = Column(Integer)
    hari             = Column(Integer)
    npwpd            = Column(String(32))
    jth_tempo        = Column(Date) 
    is_kota          = Column(SmallInteger)
    created  = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated  = Column(DateTime, nullable=True)
    create_uid  = Column(Integer, nullable=False, default=1)
    update_uid  = Column(Integer, nullable=True)
    UniqueConstraint('tahun', 'unit_kd', 'kode',
                name = 'arinvoice_ukey')

class ARPaymentTrans(DefaultModel, Base):
    __tablename__  = 'ar_payment_trans'
    __table_args__ = {'extend_existing':True, 'schema' : schematbl,}
    tahun           = Column(Integer, nullable=False)
    unit_kd         = Column(String,  nullable=False) 
    unit_nm         = Column(String(128))
    kode            = Column(String(50)) # no sspd
    nama            = Column(String(255)) # nama pembayar
    alamat          = Column(String(255)) 
    uraian          = Column(String(255)) #uraian payment
    tgl_trans       = Column(Date)    
    tgl_validasi    = Column(Date)
    rekening_kd     = Column(String(16))
    rekening_nm     = Column(String(128))
    pokok           = Column(BigInteger)
    denda           = Column(BigInteger)
    bunga           = Column(BigInteger)
    nilai           = Column(BigInteger, nullable=False)
    #status          = Column(SmallInteger, nullable=False, default=0)
    sumber_id       = Column(SmallInteger, default=1)#1, 2, 3, 4
    sumber_nm       = Column(String(16))#1, 2, 3, 4
    posted          = Column(SmallInteger, nullable=False, default=0)
    ref_kode         = Column(String(32), unique=True) # no bayar
    ref_nama         = Column(String(64)) # nama wp
    kecamatan_kd     = Column(String(32))
    kecamatan_nm     = Column(String(64))
    kelurahan_kd     = Column(String(32))
    kelurahan_nm     = Column(String(64))
    tahun            = Column(Integer)
    bulan            = Column(Integer)
    minggu           = Column(Integer)
    hari             = Column(Integer)
    npwpd            = Column(String(32)) 
    jth_tempo        = Column(Date) 
    is_kota          = Column(SmallInteger)
    created  = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated  = Column(DateTime, nullable=True)
    create_uid  = Column(Integer, nullable=False, default=1)
    update_uid  = Column(Integer, nullable=True)
    UniqueConstraint('tahun', 'unit_kd', 'kode',
                name = 'ar_payment_trans_ukey')


class ARInvoicePbb(DefaultModel, Base):
    __tablename__  = 'ar_invoice_pbb'
    __table_args__ = {'extend_existing':True, 'schema' : schematbl,}
    tahun           = Column(Integer, nullable=False)
    unit_kd         = Column(String,  nullable=False) 
    unit_nm         = Column(String(128))
    kode            = Column(String(50))
    nama            = Column(String(255))
    alamat          = Column(String(255))
    uraian          = Column(String(255))
    tgl_tetap       = Column(Date)    
    tgl_validasi    = Column(Date)
    rekening_kd     = Column(String(16))
    rekening_nm     = Column(String(128))
    pokok           = Column(BigInteger)
    denda           = Column(BigInteger)
    bunga           = Column(BigInteger)
    nilai           = Column(BigInteger, nullable=False)
    #status          = Column(SmallInteger, nullable=False, default=0)
    sumber_id       = Column(SmallInteger, default=1)#1, 2, 3, 4
    sumber_nm       = Column(String(16))#1, 2, 3, 4
    posted          = Column(SmallInteger, nullable=False, default=0)
    ref_kode         = Column(String(32), unique=True)
    ref_nama         = Column(String(64))
    kecamatan_kd     = Column(String(32))
    kecamatan_nm     = Column(String(64))
    kelurahan_kd     = Column(String(32))
    kelurahan_nm     = Column(String(64))
    tahun            = Column(Integer)
    bulan            = Column(Integer)
    minggu           = Column(Integer)
    hari             = Column(Integer)
    npwpd            = Column(String(32))
    jth_tempo        = Column(Date) 
    is_kota          = Column(SmallInteger)
    created  = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated  = Column(DateTime, nullable=True)
    create_uid  = Column(Integer, nullable=False, default=1)
    update_uid  = Column(Integer, nullable=True)
    UniqueConstraint('tahun', 'unit_kd', 'kode',
                name = 'arinvoice_pbb_ukey')

class ARPaymentPbb(DefaultModel, Base):
    __tablename__  = 'ar_payment_pbb'
    __table_args__ = {'extend_existing':True, 'schema' : schematbl,}
    tahun           = Column(Integer, nullable=False)
    unit_kd         = Column(String,  nullable=False) 
    unit_nm         = Column(String(128))
    kode            = Column(String(50)) # no sspd
    nama            = Column(String(255)) # nama pembayar
    alamat          = Column(String(255)) 
    uraian          = Column(String(255)) #uraian payment
    tgl_trans       = Column(Date)    
    tgl_validasi    = Column(Date)
    rekening_kd     = Column(String(16))
    rekening_nm     = Column(String(128))
    pokok           = Column(BigInteger)
    denda           = Column(BigInteger)
    bunga           = Column(BigInteger)
    nilai           = Column(BigInteger, nullable=False)
    #status          = Column(SmallInteger, nullable=False, default=0)
    sumber_id       = Column(SmallInteger, default=1)#1, 2, 3, 4
    sumber_nm       = Column(String(16))#1, 2, 3, 4
    posted          = Column(SmallInteger, nullable=False, default=0)
    ref_kode         = Column(String(32), unique=True) # no bayar
    ref_nama         = Column(String(64)) # nama wp
    kecamatan_kd     = Column(String(32))
    kecamatan_nm     = Column(String(64))
    kelurahan_kd     = Column(String(32))
    kelurahan_nm     = Column(String(64))
    tahun            = Column(Integer)
    bulan            = Column(Integer)
    minggu           = Column(Integer)
    hari             = Column(Integer)
    npwpd            = Column(String(32)) 
    jth_tempo        = Column(Date) 
    is_kota          = Column(SmallInteger)
    created  = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated  = Column(DateTime, nullable=True)
    create_uid  = Column(Integer, nullable=False, default=1)
    update_uid  = Column(Integer, nullable=True)
    UniqueConstraint('tahun', 'unit_kd', 'kode',
                name = 'ar_payment_pbb_ukey')

  
class ARPaymentPbbRekap(DefaultModel, Base):
    __tablename__  = 'ar_payment_pbb_rekap'
    __table_args__ = {'extend_existing':True, 'schema' : schematbl,}
    tahun           = Column(Integer, nullable=False)
    unit_kd         = Column(String,  nullable=False)
    thn_pajak_sppt  = Column(String(4))
    unit_nm         = Column(String(128))
    kode            = Column(String(50)) # generator PBB-YYYYYMMDD-BANKTGL-PERSESI-TP
    #ama            = Column(String(255)) # nama pembayar
    #lamat          = Column(String(255))
    uraian          = Column(String(255)) #uraian payment
    tgl_trans       = Column(Date)
    tgl_validasi    = Column(Date)
    rekening_kd     = Column(String(16))
    rekening_nm     = Column(String(128))
    pokok           = Column(BigInteger)
    denda           = Column(BigInteger)
    bunga           = Column(BigInteger)
    nilai           = Column(BigInteger, nullable=False)
    #status          = Column(SmallInteger, nullable=False, default=0)
    sumber_id       = Column(SmallInteger, default=1)#1, 2, 3, 4
    sumber_nm       = Column(String(16))#1, 2, 3, 4
    posted          = Column(SmallInteger, nullable=False, default=0)
    #ef_kode         = Column(String(32), unique=True) # no bayar
    #ef_nama         = Column(String(64)) # nama wp
    #ecamatan_kd     = Column(String(32))
    #ecamatan_nm     = Column(String(64))
    #elurahan_kd     = Column(String(32))
    #elurahan_nm     = Column(String(64))
    #ahun            = Column(Integer)
    #ulan            = Column(Integer)
    #inggu           = Column(Integer)
    #ari             = Column(Integer)
    #pwpd            = Column(String(32))
    #th_tempo        = Column(Date)
    is_kota          = Column(SmallInteger)
    created  = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated  = Column(DateTime, nullable=True)
    create_uid  = Column(Integer, nullable=False, default=1)
    update_uid  = Column(Integer, nullable=True)
    UniqueConstraint('tahun', 'unit_kd', 'kode',
            name = 'ar_payment_pbb_rekap_ukey')
    
class ARInvoiceBphtb(DefaultModel, Base):
    __tablename__  = 'ar_invoice_bphtb'
    __table_args__ = {'extend_existing':True, 'schema' : schematbl,}
    tahun           = Column(Integer, nullable=False)
    unit_kd         = Column(String,  nullable=False) 
    unit_nm         = Column(String(128))
    kode            = Column(String(50))
    nama            = Column(String(255))
    alamat          = Column(String(255))
    uraian          = Column(String(255))
    tgl_tetap       = Column(Date)    
    tgl_validasi    = Column(Date)
    rekening_kd     = Column(String(16))
    rekening_nm     = Column(String(128))
    pokok           = Column(BigInteger)
    denda           = Column(BigInteger)
    bunga           = Column(BigInteger)
    nilai           = Column(BigInteger, nullable=False)
    #status          = Column(SmallInteger, nullable=False, default=0)
    sumber_id       = Column(SmallInteger, default=1)#1, 2, 3, 4
    sumber_nm       = Column(String(16))#1, 2, 3, 4
    posted          = Column(SmallInteger, nullable=False, default=0)
    ref_kode         = Column(String(32), unique=True)
    ref_nama         = Column(String(64))
    kecamatan_kd     = Column(String(32))
    kecamatan_nm     = Column(String(64))
    kelurahan_kd     = Column(String(32))
    kelurahan_nm     = Column(String(64))
    tahun            = Column(Integer)
    bulan            = Column(Integer)
    minggu           = Column(Integer)
    hari             = Column(Integer)
    npwpd            = Column(String(32))
    jth_tempo        = Column(Date) 
    is_kota          = Column(SmallInteger)
    created  = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated  = Column(DateTime, nullable=True)
    create_uid  = Column(Integer, nullable=False, default=1)
    update_uid  = Column(Integer, nullable=True)
    UniqueConstraint('tahun', 'unit_kd', 'kode',
                name = 'arinvoice_bphtb_ukey')

class ARPaymentBphtb(DefaultModel, Base):
    __tablename__  = 'ar_payment_bphtb'
    __table_args__ = {'extend_existing':True, 'schema' : schematbl,}
    tahun           = Column(Integer, nullable=False)
    unit_kd         = Column(String,  nullable=False) 
    unit_nm         = Column(String(128))
    kode            = Column(String(50)) # no sspd
    nama            = Column(String(255)) # nama pembayar
    alamat          = Column(String(255)) 
    uraian          = Column(String(255)) #uraian payment
    tgl_trans       = Column(Date)    
    tgl_validasi    = Column(Date)
    rekening_kd     = Column(String(16))
    rekening_nm     = Column(String(128))
    pokok           = Column(BigInteger)
    denda           = Column(BigInteger)
    bunga           = Column(BigInteger)
    nilai           = Column(BigInteger, nullable=False)
    #status          = Column(SmallInteger, nullable=False, default=0)
    sumber_id       = Column(SmallInteger, default=1)#1, 2, 3, 4
    sumber_nm       = Column(String(16))#1, 2, 3, 4
    posted          = Column(SmallInteger, nullable=False, default=0)
    ref_kode         = Column(String(32), unique=True) # no bayar
    ref_nama         = Column(String(64)) # nama wp
    kecamatan_kd     = Column(String(32))
    kecamatan_nm     = Column(String(64))
    kelurahan_kd     = Column(String(32))
    kelurahan_nm     = Column(String(64))
    tahun            = Column(Integer)
    bulan            = Column(Integer)
    minggu           = Column(Integer)
    hari             = Column(Integer)
    npwpd            = Column(String(32)) 
    jth_tempo        = Column(Date) 
    is_kota          = Column(SmallInteger)
    created  = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated  = Column(DateTime, nullable=True)
    create_uid  = Column(Integer, nullable=False, default=1)
    update_uid  = Column(Integer, nullable=True)
    UniqueConstraint('tahun', 'unit_kd', 'kode',
                name = 'ar_payment_bphtb_ukey')
                                    
