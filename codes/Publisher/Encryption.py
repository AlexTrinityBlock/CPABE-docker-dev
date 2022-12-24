from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,GT,pair
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.ABEncMultiAuth import ABEncMultiAuth
from charm.schemes.abenc.abenc_dacmacs_yj14 import DACMACS
from charm.core.engine.util import objectToBytes,bytesToObject
from StringEncode import StringEncode
import json

class Encryption:

    def encrypt(self,message:str):
        string_encode = StringEncode()
        message_int:int = string_encode.string_to_integer(message)

        dac = DACMACS(PairingGroup('SS512'))
        GPP, GMK = dac.setup()

        users = {} # public user data
        authorities = {}

        authorityAttributes = ["ONE", "TWO", "THREE", "FOUR"]
        authority1 = "authority1"
        policy_str = '((ONE or THREE) and (TWO or FOUR))'

        dac.setupAuthority(GPP, authority1, authorityAttributes, authorities)

        alice = { 'id': 'alice', 'authoritySecretKeys': {}, 'keys': None }
        alice['keys'], users[alice['id']] = dac.registerUser(GPP)

        bob = { 'id': 'bob', 'authoritySecretKeys': {}, 'keys': None }
        bob['keys'], users[bob['id']] = dac.registerUser(GPP)

        for attr in authorityAttributes[0:-1]:
            dac.keygen(GPP, authorities[authority1], attr, users[alice['id']], alice['authoritySecretKeys'])
            dac.keygen(GPP, authorities[authority1], attr, users[bob['id']], bob['authoritySecretKeys'])

        # Generate A String for AES Key
        AES_key_before_serialization  = PairingGroup('SS512').random(GT)
        CT = dac.encrypt(GPP, policy_str, AES_key_before_serialization, authorities[authority1])
        cipher_AES_key = objectToBytes(CT, PairingGroup('SS512')).decode("utf-8")

        return cipher_AES_key