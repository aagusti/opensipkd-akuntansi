from config import db_url_src, rpc_url
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

from config import (db_url_dst)

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
    
eng_src = create_engine(db_url_src)
eng_src.echo=True

sql = ("""SELECT tahun, kode rekening_kd, nama, '1.20.05' unit_kd, ref_kode, ref_nama, to_char(tanggal,'YYYY-MM-DD') tanggal, amount, 
              kecamatan_kd, kecamatan_nm, kelurahan_kd, kelurahan_nm, is_kota, 
              sumber_id, sumber_data
          FROM apbd.ar_invoice_item 
          WHERE tanggal = TO_DATE('{tanggal}','YYYY-MM-DD')""").format(tanggal=tanggal)
          
rows = eng_src.execute(sql)
row_dicted = [dict(row) for row in rows]
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
rows = requests.post(rpc_url, data=jsondata,headers=headers)
row_dicted = json.loads(rows.text)
info("Invoice:", row_dicted)
info('Selesai')          
os.remove(pid_file)
