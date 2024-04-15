from mnemonic import Mnemonic
import hashlib
import base58
import requests

# Mnemonic("english").generate(strength=128)
checked = 0
balancecheck = 0
addresses = ""
mnemonics = ""
def public_key_to_address(public_key):
    # Perform SHA-256 hashing on the public key
    sha = hashlib.sha256()
    sha.update(public_key.encode())
    public_key_hash = sha.digest()

    # Perform RIPEMD-160 hashing on the result of SHA-256
    rip = hashlib.new('ripemd160')
    rip.update(public_key_hash)
    key_hash = rip.digest()

    # Add version byte in front of RIPEMD-160 hash (0x00 for Main Network)
    modified_key_hash = b'\x00' + key_hash

    # Perform SHA-256 hashing on the modified RIPEMD-160 hash
    sha_2 = hashlib.sha256()
    sha_2.update(modified_key_hash)
    sha_2_hex = sha_2.hexdigest()

    # Perform SHA-256 hashing on the result of the previous SHA-256 hash
    sha_3 = hashlib.sha256()
    sha_3.update(sha_2.digest())
    sha_3_hex = sha_3.hexdigest()

    # Take the first 4 bytes of the second SHA-256 hash, this is the address checksum
    checksum = sha_3_hex[:8]

    # Add the 4 checksum bytes from stage 8 at the end of extended RIPEMD-160 hash from stage 5
    byte_25_address = modified_key_hash + bytes.fromhex(checksum)

    # Convert the result from a byte string into a base58 string using Base58Check encoding
    address = base58.b58encode(byte_25_address).decode('utf-8')

    return address
def get_address_info(addresses,mnemonics):
    data = requests.get(f'https://blockchain.info/balance?active={addresses}').json()
    # create the address list 
    addresses = addresses[1:]
    addresses = addresses.replace('|', ' ')
    words=addresses.split(' ')
    # create the mnemonic list 
    mnemonics = mnemonics[1:]
    listmnemo = mnemonics.split("|")
    # print(mnemonics)
    # print(words)
    for i in range(len(words)) :
        # print("address :" ,words[i])
        balance = data[words[i]]['final_balance'] / 100000000  # convert satoshi to BTC
        if (balance > 0):
            print(f'Balance: {balance} BTC')
            print(listmnemo[i])



while checked < 100 :
    checked += 1
    balancecheck = 0
    while balancecheck < 11:

        mnemo = Mnemonic("english").generate(strength=128)
        print("wallet checked ", checked, " : ", mnemo)

        private_key = private_key = Mnemonic.to_seed(mnemo, passphrase='')
        # print(private_key)

        public_key = Mnemonic.to_hd_master_key(private_key)
        # print(public_key)
        # list of addresses
        address = public_key_to_address(public_key)
        addresses = addresses + "|" + address
        # list of mnemonic
        mnemonics = mnemonics + "|" + mnemo

        # print(addresses)

        checked += 1
        balancecheck += 1
    get_address_info(addresses,mnemonics)

    

