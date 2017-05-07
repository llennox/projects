
import struct
from binascii import unhexlify, crc32

f = open('encoded.txt','r')

data = b''
for ff in f.readlines():
chunks = ff.split(' ')
for c in chunks:
if 'O' not in c and '\n' not in c:
data += unhexlify(c.encode('utf8'))

print data

length = struct.unpack('<L', data[0:4])[0]
checksum = struct.unpack('<L', data[4:8])[0]
data = data[8:8+length]
