"""
This is a python3 script

Sample Merge Mining Program, must be run from directory where src/ and test_framework/ lives
Make sure to have a Bitcoin Stash full node running and change variables RPC_USER, RPC_PASS,
RPC_IP, and RPC_PORT to connect to it
"""

import sys
import time
import struct

if sys.version_info < (3,0):
    raise Exception("Must use Python3")

from test_framework.mininode import uint256_from_compact, ser_uint256, ser_uint256_vector, uint256_from_str, hash256
from test_framework.util import hex_str_to_bytes, bytes_to_hex_str
from test_framework.blocktools import create_coinbase, create_block
from test_framework.authproxy import AuthServiceProxy
from test_framework.auxpow import CAuxPow

"""
Setup RPC Connection with BitcoinStash node
"""
RPC_USER ='test'
RPC_PASS = 'test'
RPC_IP = '127.0.0.1'
RPC_PORT = '10202'

def bstash_connect():
    url="http://%s:%s@%s:%s"%(RPC_USER, RPC_PASS, RPC_IP, RPC_PORT)
    return AuthServiceProxy(url)

bstash = bstash_connect()

"""
Create BStash address, Make call to createauxblock, this will get us all the data needed
for merge mining
"""
address = bstash.getnewaddress()
aux = bstash.createauxblock(address)

"""
Construct BCash Block, making sure that we insert aux['auxpowcoinbasedata'] into the conibase script sig,
and than solve the block at the Bitcoin Stash difficulty. This process will be different for everyone...
In the below example, we'll just construct a random block and solve it slowly via python
"""
height = 5
coinbase = create_coinbase(height)
script_sig = aux['auxpowcoinbasedata']

# Construct coinbase tx in BCash block
coinbase.vin[0].scriptSig = hex_str_to_bytes(script_sig)
previous_blockhash='000000000758eb8a22332a2c32c671e0489d56262bf659774421f37d58f6550c'
coinbase.rehash()
block = create_block(int(previous_blockhash, 16), coinbase)
block.hashMerkleRoot = block.calc_merkle_root()
block.rehash()

# Get the difficulty on the BStash chain
hex_bits = aux['bits']
nBits = struct.unpack(">I", hex_str_to_bytes(hex_bits))[0]
target = uint256_from_compact(nBits)

# Construct BCash block
block_ser = b""
block_ser += struct.pack("<i", block.nVersion)
block_ser += ser_uint256(block.hashPrevBlock)
block_ser += ser_uint256(block.hashMerkleRoot)
block_ser += struct.pack("<I", block.nTime)
block_ser += struct.pack("<I", block.nBits)
block_ser_final = block_ser + struct.pack("<I", block.nNonce)
hash_result = uint256_from_str(hash256(block_ser_final))

print("Starting mining, difficulty:{}".format(hex_bits))
i = 0
start_time = time.time()
maxnonce = 2**32
block.nNonce = 0
nNonce = 0
while hash_result > target:
    nNonce +=1
    if nNonce >= maxnonce:
        print("Finished mining:{} per sec".format(nNonce/(time.time()-start_time)))
        sys.exit()
    hash_result = uint256_from_str(hash256(block_ser + struct.pack("<I", nNonce)))

block.nNonce = nNonce
block.sha256 = hash_result
print("Finished mining:{} per sec".format(block.nNonce/(time.time()-start_time)))

"""
Construct auxpow data and submit it to the BitcoinStash network via submitauxblock
verify that our block got accepted
"""
# Construct Auxpow data
auxpow = CAuxPow()
auxpow.tx = coinbase
auxpow.hashBlock = block.sha256
auxpow.vMerkleBranch = []
auxpow.vChainMerkleBranch = []
auxpow.nChainIndex = 0
auxpow.parentBlock = block

# Submit Auxpow data, make sure it worked
before_blocks = bstash.getinfo()['blocks']
result = bstash.submitauxblock(aux['hash'], auxpow.serialize().hex())
print("Bstash submitauxblock result: {}".format(result))
if bstash.getinfo()['blocks'] == before_blocks+1:
    print("Succeeded in incrementing an auxpow block")
else:
    print("Failed to increment auxpow block for some reason")


