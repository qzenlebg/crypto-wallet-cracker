from mnemonic import Mnemonic
import hashlib
import base58
import requests
import time
import os
import json


print("""
 _____                                _                    _ _     _                      _           \r
|     |___ ___ ___    ___ ___ _ _ ___| |_ ___    _ _ _ ___| | |___| |_    ___ ___ ___ ___| |_ ___ ___ \r
|  |  |- _| -_|   |  |  _|  _| | | . |  _| . |  | | | | .'| | | -_|  _|  |  _|  _| .'|  _| '_| -_|  _|\r
|__  _|___|___|_|_|  |___|_| |_  |  _|_| |___|  |_____|__,|_|_|___|_|    |___|_| |__,|___|_,_|___|_|  \r
   |__|                      |___|_|                                                                  \r""")

input("Press Enter to start program ...")

# variables can be modified in the settings.json file
with open(r"settings.json", 'r') as f:
    config = json.load(f)    
# config = json.load(open('settings.json', "r"))

checked = config['checked']
speed = config["speed"]
x = config["x"] # every x mnemonics it verifies max:100 recomended:50

def saveconfig(config,checked,speed):
    config["checked"] = checked
    config["speed"] = speed
    json.dump(config,open('settings.json', 'w'))
    # json.dumps({
    # 'checked':checked,
    # 'x': 50,
    # "speed":speed
    # },open('settings.json',"w"))
    print("saved checked")

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

def request(stringaddress,listaddresses,mnemonics):
    try: # first method to verify
        data = requests.get(f'https://blockchain.info/balance?active={stringaddress}').json()
        for i in range(len(listaddresses)) :
            balance = data[listaddresses[i]]['final_balance'] / 100000000  # convert satoshi to BTC
            if (balance > 0):
                print(f'Balance: {balance} BTC')
                print(mnemonics[i])
                file = open('wallets.txt', 'a')
                file.write("wallet : "+ mnemonics[i]+"\n")
                file.close()
    except:
        print("Error will restart program in 5 seconds")
        time.sleep(1)
        for x in range (0,5):  
            print ("Loading " + "." * x, end="\r")
            time.sleep(1)
        try:
            request(stringaddress,listaddresses,mnemonics)
        except:
            exec(open('Qzen.py').read())
            time.sleep(3)
            quit()

        
def get_address_info(addresses,mnemonics):
    stringaddress = '|'.join(addresses)
    request(stringaddress,addresses,mnemonics)



while True :
    mnemonics = []
    addresses = []
    while checked < ((checked // x) + ((checked % x != 0) * 1)) * x: # every X mnemonic it verifys the wallet
        mnemo = Mnemonic("english").generate(strength=128)
        print("wallet checked ", checked, " : ", mnemo)

        private_key = private_key = Mnemonic.to_seed(mnemo, passphrase='')
        # print(private_key)

        public_key = Mnemonic.to_hd_master_key(private_key)
        # print(public_key)

        # list of addresses
        address = public_key_to_address(public_key)
        addresses.append(address)
        time.sleep(speed)
        # list of mnemonic
        mnemonics.append(mnemo)
        checked += 1
    saveconfig(config,checked,speed)
    checked += 1
    get_address_info(addresses,mnemonics)
