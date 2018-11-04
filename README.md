BitcoinStash Merge Mining Guide
===========================

## Overview

Bitcoin Stash is a merge mineable cryptocurrency that utilizes SHA256 for its mining algorithm. This means that it can be merge mined with other SHA256 coins like Bitcoin an Bitcoin Cash. Merge mining is a process where a miner is able to mine multiple cryptocurrencies at the same time. All that is required for a miner is to add 48 bytes of data to the coinbase of the parent block.

We will have a private testnet testing phase beginning at 11/4/18. On 11/4/18, miners will have access to Bitcoin Stash binaries (with only testnet capabilities available). They will be able to merge mine on the testnet by following the below instructions. A sample code implementation is provided in bitcoinstash_mergemining_sample.py.

## Instructions

Follow the step belows to merge mine on Bitcoin Stash. Sample code implementation is provided in bitcoinstash_mergemining_sample.py.

1) Use RPC call getnewaddress() to get a new address for Bitcoin Stash (this will only need to be done once)
2) Call RPC command createauxblock() with address obtained from step 1). This will make a Bitcoin Stash block with a coinbase payment to the address.
3) From the JSON output of createauxblock(), use 'auxcoinbasedata' to obtain the data that must be inserted into the script sig of the coinbase in the parent block. To understand how this data is constructed, read the 'Constructing the Auxpow Coinbase Data' section below.
4) Start solving the parent block until you meet the [encoded target threshold](https://bitcoin.org/en/glossary/nbits) specified by the 'bits' field in the JSON output of createauxblock().
5) If the parent block meets the target as defined step 4, construct the auxpow header data. Submit the auxpow header data using RPC command submitauxblock() with first argument being 'hash' from output of createauxblock in step 2), the second argument is the hex string of the auxpow data. Instructions on constructing the auxpow data is shown below. If a valid auxpow header data was submitted, the merge mined block will be submitted on the Bitcoin Stash network.


## Constructing the Auxpow Header Data

Auxpow header data is extra data attached to the BitcoinStash block header that links the block to the the parent block. It is composed from the below data.

Serialized coinbase transaction +
Hash of the parent block (32 bytes) +
Merkle branches (can be 0x00, if only transaction in block) +
Index in the merkle branch (4 bytes, must always be \x00\x00\x00\x00) +
Chain Merkle branch (4 bytes, can be 0x00, if no other child chain) +
Index in the chain merkle branch (4 bytes, can be \x00\x00\x00\x00 if no other child chain) +
Serialized parent block header

## Constructing the Auxpow Coinbase Data

The auxpow coinbase data is data inserted into the parent block's coinbase to link the parent block to the BitcoinStash block. It is composed from the below data.

Merge Mining Header (4 bytes, must always be \xFA\xBE\x6D\x6D ) +
Root hash of Merkle Trie containing child chian (32 bytes, set to hash of Bitcoin Stash block if no other child chain) +
Merkle Trie Size, (4 bytes, set to 1 if no other child chain) +
Nonce, the nonce and the chain id of the child chain determines a pseudo random slot in the chain merkle trie (4 bytes, can be set to anything if no other child chain) +
Parent Chain Id (4 bytes, set to 210 if Bitcoin is the parent block 209 if Bitcoin Cash is parent block)

## Stand Alone Mining

Stand alone mining (mining Bitcoin Stash only without using its merge mining capabilities), will also be possible through the standard RPC call getblocktemplate.

