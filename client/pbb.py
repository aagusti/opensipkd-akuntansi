import hmac
import hashlib
import base64
import json
import requests
from datetime import datetime


filenm = 'export-pbb'
pid_file = '/var/run/%s.pid' % filenm
pid = demon.make_pid(pid_file)
log = demon.Log('/var/log/%s.log' % filenm)

arg = sys.argv[0]
c = len(sys.argv) 
print c
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
    #file = 
    if fileExtension == '.csv': # and fileName[:3]<>'PBB':
        with open('%s/%s' %(path,file), 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in spamreader:
                c = row.count
                datas = {}    
                try:
                    datas['kode']         = row and row[0] and row[ 0].strip() or None
                    datas['nama']         = row and row[1] and row[ 1].strip() or None
                    datas['tahun']        = row and row[2] and row[ 2].strip() or None
                    datas['amount']       = row and row[3] and row[ 3].strip() or None       
                    datas['ref_kode']     = row and row[4] and row[ 4].strip() or None
                    datas['ref_nama']     = row and row[5] and row[ 5].strip() or None
                    datas['tanggal']      = row and row[6] and row[ 6].strip() or None          
                    datas['kecamatan_kd'] = row and c > 7  and row[ 7].strip() or None          
                    datas['kecamatan_nm'] = row and c > 8  and row[ 8].strip() or None          
                    datas['kelurahan_kd'] = row and c > 9  and row[ 9].strip() or None          
                    datas['kelurahan_nm'] = row and c > 10 and row[10].strip() or None          
                    datas['is_kota']      = row and c > 11 and row[11].strip() or None          
                    datas['sumber_data']  = row and c > 12 and row[12].strip() or None          
                    datas['sumber_id']    = row and c > 13 and row[13].strip() or None          
                except:
                    print path,file
                    os.rename('%s/%s' %(path,file), '/home/eis/error/%s' % (file))
                    sys.exit()
                # print datas
                # print datas['kode']
                
                try:
                    if data_found(datas):
                        update(datas)
                    else:
                        insert(datas)
                except:
                    pass
            # csvfile.cose()                          
            os.rename('%s/%s' %(path,file), '/home/eis-bak/%s-%s.bak' % (file, datetime.now()))   
info('Selesai')          
os.remove(pid_file)


#def __main__():
headers = generate_header('admin','$2a$10$g4uTd8xjqP183whcYEGyOesblGljO9AErnpCTJDH0SEUBkHXTLM5C')
datas={"data":[{'kode':1},{'kode':2}]}
data = {
      "jsonrpc": "2.0",
      "method": "set_invoice",
      "params": datas,
      "id":1
    }
print data        
jsondata=json.dumps(data, ensure_ascii=False)        
url = "http://localhost:6543/ws"
rows = requests.post(url, data=jsondata,headers=headers)
row_dicted = json.loads(rows.text)
print "Invoice:", row_dicted

headers = generate_header('admin','$2a$10$g4uTd8xjqP183whcYEGyOesblGljO9AErnpCTJDH0SEUBkHXTLM5C')
datas={"data":[{'kode':1},{'kode':2}]}
data = {
      "jsonrpc": "2.0",
      "method": "set_payment",
      "params": datas,
      "id":1
    }
print data        
jsondata=json.dumps(data, ensure_ascii=False)        
url = "http://localhost:6543/ws"
rows = requests.post(url, data=jsondata,headers=headers)
row_dicted = json.loads(rows.text)
print "Payment:", row_dicted
