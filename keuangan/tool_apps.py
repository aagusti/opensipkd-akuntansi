PROPINSI = [('kd_propinsi', 2, 'N'),]

DATI2 = list(PROPINSI)
DATI2.append(('kd_dati2', 2, 'N'))

KECAMATAN = list(DATI2)
KECAMATAN.append(('kd_kecamatan', 3, 'N'))

KELURAHAN = list(KECAMATAN)
KELURAHAN.append(('kd_kelurahan', 3, 'N'))
    
BLOK = list(KELURAHAN)
BLOK.append(('kd_blok', 3, 'N'))
    
NOP = list(BLOK)

NOP.append(('no_urut', 4, 'N'))
NOP.append(('kd_jns_op', 1, 'N'))
    
SPPT  = list(NOP)

SPPT.append(('thn_pajak_sppt', 4, 'N'))
BAYAR = list(SPPT)
BAYAR.append(('pembayaran_sppt_ke',3,'N'))    

SIKLUS = list(NOP)
SIKLUS.append(('thn_pajak_sppt', 4, 'N'))
SIKLUS.append(('siklus_sppt',3,'N'))

BANK = [
    ('kd_kanwil', 2, 'N'),
    ('kd_kantor', 2, 'N'),
    ('kd_tp', 2, 'N'),]
    
JENIS_ID = (
    (1, 'Tagihan'),
    (2, 'Piutang'),
    (3, 'Ketetapan'))


SUMBER_ID = (
    (4, 'Manual'),
    (1, 'PBB'),
    )    