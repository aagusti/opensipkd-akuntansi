from config import db_url_pbb, rpc_url
import os
import demon
import sys

from sqlalchemy import create_engine
from sqlalchemy.sql.expression import text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import DatabaseError
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Sequence

from datetime import datetime

import requests
import json
from tools import humanize_time, print_log, eng_profile, stop_daemon, json_rpc_header

def info(s):
    print_log(s)
    log.info(s)
    
def error(s):
    print_log(s, 'ERROR')
    log.error(s)   
    
filenm = 'export-pbb'
pid_file = '/var/run/%s.pid' % filenm
pid = demon.make_pid(pid_file)
log = demon.Log('/var/log/%s.log' % filenm)

arg = sys.argv[0]
c = len(sys.argv) 

if c > 1:
    tanggal = sys.argv[1]
else:
    tanggal = datetime.now().strftime('%Y-%m-%d')

info('Tanggal {tanggal}'.format(tanggal=tanggal))
    
eng_src = create_engine(db_url_pbb)
##eng_src.echo=True
sql = """
          SELECT * FROM ref_kelurahan 
         ORDER BY kd_propinsi, kd_dati2, kd_kecamatan, kd_kelurahan
      """
row_kels = eng_src.execute(sql)
if not row_kels:
    sys.exit()
for row_kel in row_kels:
    sql = ("""SELECT s.thn_pajak_sppt tahun, '4.1.1.12.01' rekening_kd, 'PBB P2' nama, '1.20.05' unit_kd, 
              s.kd_propinsi||s.kd_dati2||s.kd_kecamatan||s.kd_kelurahan||s.kd_blok||s.no_urut||
              s.kd_jns_op||'-'||s.thn_pajak_sppt||'-'||s.siklus_sppt ref_kode, 
              s.nm_wp_sppt ref_nama, to_char(s.tgl_terbit_sppt,'YYYY-MM-DD') tanggal, 
              s.pbb_yg_harus_dibayar_sppt amount, 
              kec.kd_kecamatan kecamatan_kd, kec.nm_kecamatan kecamatan_nm, 
              kel.kd_kelurahan kelurahan_kd, kel.nm_kelurahan kelurahan_nm, 
              case when kel.kd_sektor='20' then 1 else 0 end is_kota, 
              2 sumber_id, 'PBB' sumber_data
          FROM sppt s 
               inner join ref_kelurahan kel 
                          on s.kd_propinsi=kel.kd_propinsi and
                             s.kd_dati2=kel.kd_dati2 and
                             s.kd_kecamatan=kel.kd_kecamatan and
                             s.kd_kelurahan=kel.kd_kelurahan
               inner join ref_kecamatan kec 
                          on s.kd_propinsi=kec.kd_propinsi and
                             s.kd_dati2=kec.kd_dati2 and
                             s.kd_kecamatan=kec.kd_kecamatan              
          WHERE   s.kd_propinsi ='{kd_propinsi}' and
                  s.kd_dati2    ='{kd_dati2}' and
                  s.kd_kecamatan='{kd_kecamatan}' and
                  s.kd_kelurahan='{kd_kelurahan}'
                  AND s.tgl_terbit_sppt = TO_DATE('{tanggal}','YYYY-MM-DD')""")\
          .format(tanggal=tanggal,
                  kd_propinsi=row_kel.kd_propinsi, 
                  kd_dati2=row_kel.kd_dati2, 
                  kd_kecamatan=row_kel.kd_kecamatan, 
                  kd_kelurahan=row_kel.kd_kelurahan)
          
    rows = eng_src.execute(sql).fetchall()
    print row_kel.nm_kelurahan, len(rows)
    if len(rows)==0:
        continue
    row_dicted = [dict(row) for row in rows]
    #print row_dicted
    headers = json_rpc_header('admin','$2a$10$g4uTd8xjqP183whcYEGyOesblGljO9AErnpCTJDH0SEUBkHXTLM5C')
    datas={"data":row_dicted}
    data = {
          "jsonrpc": "2.0",
          "method": "set_invoice",
          "params": datas,
          "id":1
        }
        
    jsondata=json.dumps(data, ensure_ascii=False)        
    info('Mulai')          
    try:
        rows = requests.post(rpc_url, data=jsondata,headers=headers)
    except:
        sys.exit()
    row_dicted = json.loads(rows.text)
    info("Invoice: {data}".format(data=row_dicted))
    #sys.exit()
info('Selesai')          
os.remove(pid_file)
