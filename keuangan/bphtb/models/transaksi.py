from datetime import datetime
from sqlalchemy import(
    Column,
    Integer,
    BigInteger,
    SmallInteger,
    Float,
    Text,
    DateTime,
    String,
    ForeignKey,
    text,
    UniqueConstraint,
    )
    
from sqlalchemy.orm import(
    relationship,
    backref
    )
from ...models import CommonModel
from ..models import bphtbBase, bphtbDBSession, bphtb_schema
from ...tools import get_settings

BPHTB_ARGS =  {'extend_existing':True, 
         'schema' : bphtb_schema,
        }  
      
class Perolehan(bphtbBase, CommonModel):
    __tablename__  = 'bphtb_perolehan'
    __table_args__ = (BPHTB_ARGS)    
    id  = Column(Integer, primary_key=True)
    nama = Column(String(100))
    npoptkp = Column(BigInteger, nullable=False)
    pengurang = Column(Integer)
    singkatan = Column(String(20))

class Ppat(bphtbBase, CommonModel):
    __tablename__  = 'bphtb_ppat'
    __table_args__ = (UniqueConstraint('kode', 
                          name='bphtb_ppat_kode_uk'),
                      BPHTB_ARGS)    
    
    id = Column(Integer, primary_key=True)
    kode = Column(String(6))
    nama = Column(String(50))
    alamat = Column(String(50))
    kelurahan = Column(String(50))
    kecamatan = Column(String(50))
    kota = Column(String(50))
    wilayah_kerja = Column(String(50))
    kd_wilayah = Column(String(4))
    no_telp = Column(String(20))
    no_fax = Column(String(20))
    no_sk = Column(String(30))
    tgl_sk = Column(DateTime(timezone=False))
    create_uid = Column(String(20))
    update_uid = Column(String(20))
    created = Column(DateTime(timezone=False))
    updated = Column(DateTime(timezone=False))
    npwp = Column(String(20))
    pejabat_id = Column(Integer)
  
class SaldoAwal(bphtbBase, CommonModel):
    __tablename__  = 'saldo_awal'
    __table_args__ = BPHTB_ARGS    

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
                      
                      
class SspdBphtb(bphtbBase):
    __tablename__ = 'bphtb_sspd'
    __table_args__= (UniqueConstraint('tahun', 'kode',  'no_sspd', 
                                      name='bphtb_sspd_tahun_kode_no_sspd_key'),
                     BPHTB_ARGS)
    id                          = Column(BigInteger, nullable=False, primary_key=True)
    tahun                       = Column(Integer, nullable=False)
    kode                        = Column(String(1), nullable=False)
    no_sspd                     = Column(BigInteger, nullable=False)
    ppat_id                     = Column(Integer, ForeignKey("bphtb.bphtb_ppat.id"))
    wp_nama                     = Column(String(50), nullable=False)
    wp_npwp                     = Column(String(50), nullable=False)
    wp_alamat                   = Column(String(100), nullable=False)
    wp_blok_kav                 = Column(String(100), nullable=False)
    wp_kelurahan                = Column(String(30), nullable=False)
    wp_rt                       = Column(String(3), nullable=False)
    wp_rw                       = Column(String(3), nullable=False)
    wp_kecamatan                = Column(String(30), nullable=False)
    wp_kota                     = Column(String(30), nullable=False)
    wp_provinsi                 = Column(String(30), nullable=False)
    wp_identitas                = Column(String(50), nullable=False)
    wp_identitaskd              = Column(String(50))
    tgl_transaksi               = Column(DateTime(timezone=False), nullable=False)
    kd_propinsi                 = Column(String(2), nullable=False)
    kd_dati2                    = Column(String(2), nullable=False)
    kd_kecamatan                = Column(String(3), nullable=False)
    kd_kelurahan                = Column(String(3), nullable=False)
    kd_blok                     = Column(String(3), nullable=False)
    no_urut                     = Column(String(4), nullable=False)
    kd_jns_op                   = Column(String(1), nullable=False)
    thn_pajak_sppt              = Column(String(4), nullable=False)
    op_alamat                   = Column(String(100), nullable=False)
    op_blok_kav                 = Column(String(100), nullable=False)
    op_rt                       = Column(String(3), nullable=False)
    op_rw                       = Column(String(3), nullable=False)
    bumi_luas                   = Column(BigInteger, nullable=False)
    bumi_njop                   = Column(BigInteger, nullable=False)
    bng_luas                    = Column(BigInteger, nullable=False)
    bng_njop                    = Column(BigInteger, nullable=False)
    no_sertifikat               = Column(String(30))
    njop                        = Column(BigInteger, nullable=False)
    perolehan_id                = Column(Integer, ForeignKey("bphtb.bphtb_perolehan.id"),nullable=False)
    npop                        = Column(BigInteger, nullable=False)
    npoptkp                     = Column(BigInteger, nullable=False)
    tarif                       = Column(Float, nullable=False)
    terhutang                   = Column(BigInteger, nullable=False)
    bagian                      = Column(Integer, nullable=False, server_default="1")
    pembagi                     = Column(Integer, nullable=False, server_default="1")
    tarif_pengurang             = Column(Integer, nullable=False, server_default="0")
    pengurang                   = Column(BigInteger, nullable=False)
    bphtb_sudah_dibayarkan      = Column(BigInteger, nullable=False, server_default="0")
    denda                       = Column(BigInteger, nullable=False, server_default="0")
    restitusi                   = Column(BigInteger, nullable=False, server_default="0")
    bphtb_harus_dibayarkan      = Column(BigInteger, nullable=False, server_default="0")
    status_pembayaran           = Column(Integer, nullable=False, server_default="0")
    dasar_id                    = Column(Integer, nullable=False, server_default="0")
    create_uid                  = Column(String(20))
    update_uid                  = Column(String(20))
    created                     = Column(DateTime(timezone=False), nullable=False)
    updated                     = Column(DateTime(timezone=False), )
    header_id                   = Column(BigInteger, nullable=False, server_default="0")
    tgl_print                   = Column(DateTime(timezone=False))
    tgl_approval                = Column(DateTime(timezone=False))
    file1                       = Column(String(150))
    file2                       = Column(String(150))
    file3                       = Column(String(150))
    file4                       = Column(String(150))
    file5                       = Column(String(150))
    wp_kdpos                    = Column(String(5))
    file6                       = Column(String(150))
    file7                       = Column(String(150))
    file8                       = Column(String(150))
    file9                       = Column(String(150))
    file10                      = Column(String(150))
    keterangan                  = Column(String(100))
    status_daftar               = Column(Integer, server_default="0")
    persen_pengurang_sendiri    = Column(Integer, server_default="0")
    pp_nomor_pengurang_sendiri  = Column(String(50))
    no_ajb                      = Column(String(50))
    tgl_ajb                     = Column(DateTime(timezone=False))
    wp_nama_asal                = Column(String(50))
    jml_pph                     = Column(BigInteger)
    tgl_pph                     = Column(DateTime(timezone=False))
    posted                      = Column(Integer, server_default="0")
    pos_tp_id                   = Column(Integer)
    status_validasi             = Column(Integer, server_default="0")
    status_bpn                  = Column(Integer, server_default="0")
    tgl_jatuh_tempo             = Column(DateTime(timezone=False))
    verifikasi_uid              = Column(String(20))
    verifikasi_date             = Column(DateTime(timezone=False)) 
    pbb_nop                     = Column(String(24))
    verifikasi_bphtb_uid        = Column(String(20))
    verifikasi_bphtb_date       = Column(DateTime(timezone=False))
    hasil_penelitian            = Column(String(20), server_default="'Draft'")
    no_sk                       = Column(String(20))
    pengurangan_sk              = Column(String(20))
    pengurangan_jatuh_tempo_tgl = Column(DateTime(timezone=False))
    pengurangan_sk_tgl          = Column(DateTime(timezone=False))
    ketetapan_no                = Column(String(20))
    ketetapan_tgl               = Column(DateTime(timezone=False))
    ketetapan_atas_sspd_no      = Column(String(20))
    ketetapan_jatuh_tempo_tgl   = Column(DateTime(timezone=False))
    pembayaran_ke               = Column(Integer, nullable=False, server_default="1")
    mutasi_penuh                = Column(Integer, server_default="1")
    harga_transaksi             = Column(BigInteger, server_default="0")
    npopkp                      = Column(BigInteger)
    npoptkp_sudah_didapat       = Column(BigInteger, server_default="0")
    bng_luas_beban              = Column(BigInteger, server_default="0")
    bng_njop_beban              = Column(BigInteger, server_default="0")
    bumi_luas_beban             = Column(BigInteger, server_default="0")
    bumi_njop_beban             = Column(BigInteger, server_default="0")
    posted                      = Column(Integer, server_default="0")

class PembayaranBphtb(bphtbBase):
    __tablename__ = 'bphtb_bank'
    __table_args__=(UniqueConstraint('tanggal', 'jam', 'seq', 'transno', 
                          name='bphtb_bank_tanggal_jam_seq_transno_key'),
                     BPHTB_ARGS)
    id                = Column(BigInteger, nullable=False, primary_key=True)
    tanggal           = Column(DateTime, nullable=False)
    jam               = Column(DateTime(timezone=False), nullable=False)
    seq               = Column(BigInteger, nullable=False)
    transno           = Column(String(20), nullable=False)
    cabang            = Column(String(5))
    users             = Column(String(5))
    bankid            = Column(Integer, nullable=False)
    txs               = Column(String(5), nullable=False)
    sspd_id           = Column(BigInteger, ForeignKey("bphtb.bphtb_sspd.id"), nullable=False) #.format(schema=bphtb_schema)
    nop               = Column(String(50), nullable=False)
    tahun             = Column(Integer)
    kd_propinsi       = Column(String(2))
    kd_dati2          = Column(String(2))
    kd_kecamatan      = Column(String(3))
    kd_kelurahan      = Column(String(3))
    kd_blok           = Column(String(3))
    no_urut           = Column(String(4))
    kd_jns_op         = Column(String(1))
    thn_pajak_sppt    = Column(String(4))
    wp_nama           = Column(String(50), nullable=False)
    wp_alamat         = Column(String(100))
    wp_blok_kav       = Column(String(100))
    wp_rt             = Column(String(3))
    wp_rw             = Column(String(3))
    wp_kelurahan      = Column(String(30))
    wp_kecamatan      = Column(String(30))
    wp_kota           = Column(String(30))
    wp_provinsi       = Column(String(50))
    wp_kdpos          = Column(String(5))
    wp_identitas      = Column(String(50))
    wp_identitaskd    = Column(String(50))
    wp_npwp           = Column(String(50))
    notaris           = Column(String(50))
    bumi_luas         = Column(BigInteger)
    bumi_njop         = Column(BigInteger)
    bng_luas          = Column(Integer)
    bng_njop          = Column(BigInteger)
    npop              = Column(BigInteger)
    bayar             = Column(BigInteger)
    denda             = Column(Integer)
    bphtbjeniskd      = Column(Integer)
    is_validated      = Column(Integer, server_default="0")
    no_tagihan        = Column(String(50))
    catatan           = Column(String(255))
    kd_kanwil         = Column(String(2))
    kd_kantor         = Column(String(2))
    kd_bank_tunggal   = Column(String(2))
    kd_bank_persepsi  = Column(String(2))
    wp_propinsi       = Column(String(100))
    pembayaran_ke     = Column(Integer, nullable=False, server_default="1")
    posted            = Column(Integer, nullable=False, server_default="0")
    #invoice           = relationship("SspdBphtb")

# CREATE TRIGGER bphtb_bank_bi_trg
  # BEFORE INSERT
  # ON bphtb.bphtb_bank
  # FOR EACH ROW
  # EXECUTE PROCEDURE f_bphtb_bank_bi();

# -- Trigger: bphtb_bank_bu on bphtb.bphtb_bank

# -- DROP TRIGGER bphtb_bank_bu ON bphtb.bphtb_bank;

# CREATE TRIGGER bphtb_bank_bu
  # BEFORE UPDATE
  # ON bphtb.bphtb_bank
  # FOR EACH ROW
  # EXECUTE PROCEDURE f_bphtb_bank_bu();

