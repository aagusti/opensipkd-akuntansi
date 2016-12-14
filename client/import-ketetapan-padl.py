#!/usr/bin/python

import sys
from config import (db_url_dst, unit_kd, unit_id)
from tools import humanize_time, print_log, eng_profile, stop_daemon
import os
import demon
import signal
import csv
import os
import io
from time import time
from sqlalchemy import create_engine
from sqlalchemy.sql.expression import text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import DatabaseError
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Sequence
from datetime import datetime
from urllib import unquote_plus
from urlparse import urlparse
from optparse import OptionParser

def info(s):
    print_log(s)
    log.info(s)
    
def error(s):
    print_log(s, 'ERROR')
    log.error(s)    
schema = "public"    
def data_found(source):
    sql = text("""SELECT COUNT(*) C FROM {schema}.ar_invoice_trans
                  WHERE tahun = :tahun AND ref_kode = :ref_kode""".format(schema=schema)) 
    return eng_dst.execute(sql,
                        tahun          = source['tahun'],
                        ref_kode       = source['ref_kode'],).scalar()

def insert(source):
    sql = text("""INSERT INTO {schema}.ar_invoice_trans(unit_kd, kode, 
                    created,  create_uid, nama, alamat, tahun, nilai, 
                    rekening_kd, rekening_nm, ref_kode, ref_nama, tgl_tetap, kecamatan_kd, kecamatan_nm, 
                    kelurahan_kd, kelurahan_nm, is_kota, sumber_nm, sumber_id, posted, pokok,
                    denda, bunga, jth_tempo, npwpd) 
                  VALUES(:unit_kd, :kode, :created, :create_uid, 
                         :nama, :alamat, :tahun, :nilai, :rekening_kd, :rekening_nm, :ref_kode, :ref_nama, :tgl_tetap, 
                         :kecamatan_kd, :kecamatan_nm, :kelurahan_kd, :kelurahan_nm, :is_kota, 
                         :sumber_nm, :sumber_id,0, :pokok, :denda, :bunga, :jth_tempo, :npwpd)""".format(schema=schema)) 
                         
    eng_dst.execute(sql,kode           = source['kode'],
                        created        = datetime.now(),
                        #updated        = datetime.now(),
                        create_uid     = 1,
                        nama           = source['nama'],
                        alamat         = source['alamat'],
                        tahun          = source['tahun'],
                        nilai         = source['nilai'],
                        ref_kode       = source['ref_kode'],
                        rekening_kd    = source['rekening_kd'],
                        rekening_nm    = source['rekening_nm'],
                        ref_nama       = source['ref_nama'],
                        tgl_tetap        = source['tgl_tetap'],
                        kecamatan_kd   = source['kecamatan_kd'],
                        kecamatan_nm   = source['kecamatan_nm'],
                        kelurahan_kd   = source['kelurahan_kd'],
                        kelurahan_nm   = source['kelurahan_nm'],
                        is_kota        = source['is_kota'],
                        sumber_nm    = source['sumber_nm'],
                        sumber_id      = source['sumber_id'],
                        unit_kd        = source['unit_kd'],
                        pokok          = source['pokok'],
                        denda          = source['denda'],
                        bunga          = source['bunga'],
                        jth_tempo      = source['jth_tempo'],
                        npwpd          = source['npwpd'],
                    )

def update(source):
    sql = text("""UPDATE {schema}.ar_invoice_trans
                    set unit_kd        = :unit_kd,
                        kode           = :kode,
                        rekening_kd    = :rekening_kd,
                        updated        = :updated,
                        update_uid     = :update_uid,
                        nama           = :nama,
                        tahun          = :tahun,
                        nilai          = :nilai,
                        ref_kode       = :ref_kode,
                        ref_nama       = :ref_nama,
                        tgl_tetap        = :tgl_tetap,
                        kecamatan_kd   = :kecamatan_kd,
                        kecamatan_nm   = :kecamatan_nm,
                        kelurahan_kd   = :kelurahan_kd,
                        kelurahan_nm   = :kelurahan_nm,
                        is_kota        = :is_kota,
                        sumber_nm      = :sumber_nm,
                        sumber_id      = :sumber_id,
                        posted         = 0,
                        pokok          = :pokok,
                        denda          = :denda,
                        bunga          = :bunga,
                        npwpd          = :npwpd,
                        jth_tempo      = :jth_tempo
                WHERE tahun = :tahun AND kode = :kode AND ref_kode = :ref_kode""".format(schema=schema)) 
                
    eng_dst.execute(sql,  unit_kd      = source['unit_kd'],
                        kode           = source['kode'],
                        rekening_kd    = source['rekening_kd'],
                        #created        = datetime.now(),
                        updated        = datetime.now(),
                        #create_uid    = 1,
                        update_uid     = 1,
                        nama           = source['nama'],
                        tahun          = source['tahun'],
                        nilai          = source['nilai'],
                        ref_kode       = source['ref_kode'],
                        ref_nama       = source['ref_nama'],
                        tgl_tetap      = source['tgl_tetap'],
                        kecamatan_kd   = source['kecamatan_kd'],
                        kecamatan_nm   = source['kecamatan_nm'],
                        kelurahan_kd   = source['kelurahan_kd'],
                        kelurahan_nm   = source['kelurahan_nm'],
                        is_kota        = source['is_kota'],
                        sumber_nm      = source['sumber_nm'],
                        sumber_id      = source['sumber_id'],
                        pokok          = source['pokok'],
                        denda          = source['denda'],
                        bunga          = source['bunga'],
                        jth_tempo      = source['jth_tempo'],
                        npwpd          = source['npwpd'],
                    )

                    
filenm = 'import-invoice'
pid_file = '/var/run/%s.pid' % filenm
#pid = demon.make_pid(pid_file)
log = demon.Log('/home/aagusti/log/%s.log' % filenm)

arg = sys.argv[0]
c = len(sys.argv) 
#print c
#if c < 1:
#    print 'python import-csv [path]'
#    sys.exit()
    
path = "/home/eis-data/"
if c>1:
    path = sys.argv[1]

eng_dst = create_engine(db_url_dst)
eng_dst.echo=True

for file in os.listdir('%s' % path):
    fileName, fileExtension = os.path.splitext(file)
    print fileName, fileExtension 
    if fileExtension == '.csv' and fileName.find('KETETAPAN')>-1:
        print 'ada'
        with open('%s/%s' %(path,file), 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in spamreader:
                c = row.count
                datas = {}    
                try:
                    datas['unit_kd']      = unit_kd
                    datas['rekening_kd']  = row and row[0] and row[ 0].strip() or None #"4.1.1.04.05"
                    datas['rekening_nm']  = row and row[1] and row[ 1].strip() or None #"Reklame Berjalan"
                    datas['tahun']        = row and row[2] and row[ 2].strip() or None #"2015"
                    datas['nilai']        = row and row[3] and row[ 3].strip() or None #"750000"      
                    datas['nama']         = row and row[5] and row[ 5].strip() or None #"Reklame Berjalan"
                    datas['kode']         = row and row[4] and row[ 4].strip() or None #no-bayar
                    datas['ref_kode']     = row and row[18] and row[18].strip() or None #"SKP"
                    datas['ref_nama']     = row and row[5] and row[ 5].strip() or None #"IRUL TESTING"
                    datas['tgl_tetap']    = row and row[6] and row[ 6].strip() or None #"2015-01-01 00:00:00"         
                    datas['kecamatan_kd'] = row and row[7] and row[ 7].strip() or None #"01"         
                    datas['kecamatan_nm'] = row and row[8] and row[ 8].strip() or None #"PANCORAN MAS"         
                    datas['kelurahan_kd'] = row and row[9] and row[ 9].strip() or None #"006"         
                    datas['kelurahan_nm'] = row and row[10] and row[10].strip() or None #"DEPOK"      
                    datas['is_kota']      = row and row[11] and row[11].strip() or None #"1"         
                    datas['sumber_nm']    = row and row[12] and row[12].strip() or None #"PAD"         
                    datas['sumber_id']    = row and row[13] and row[13].strip() or None #"3"         
                    datas['pokok']        = row and row[14] and row[14].strip() or None #"750000"      
                    datas['denda']        = row and row[15] and row[15].strip() or None #"0"      
                    datas['bunga']        = row and row[16] and row[16].strip() or None #"0"      
                    datas['npwpd']        = row and row[17] and row[17].strip() or None #"0"      
                    datas['jth_tempo']    = row and row[19] and row[19].strip() or None #"0"      
                    datas['alamat']       = row and row[20] and row[20].strip() or None 
                except:
                    #print path,file
                    os.rename('%s/%s' %(path,file), '/home/eis-data/error/%s' % (file))
                    sys.exit()
                #try:
                if data_found(datas):
                    update(datas)
                else:
                    insert(datas)
                #except:
                #    sys.exit()
                    #pass
            # csvfile.cose()                          
        os.rename('%s/%s' %(path,file), '/home/eis-data/bak/%s' % (file)) #, datetime.now()))   
info('Selesai')          
#os.remove(pid_file)
