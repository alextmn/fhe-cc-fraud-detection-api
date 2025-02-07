from openfhe import *
import math
import os
from typing import List

PUB_KEY_DIR = 'pub-keys'

def fhe_key_gen(key_id: str):
    ClearEvalMultKeys()
    securityLevel = SecurityLevel.HEStd_128_classic

    parameters = CCParamsCKKSRNS()
    parameters.SetSecurityLevel(securityLevel)
    parameters.SetRingDim(1 << 16)
    parameters.SetKeySwitchTechnique(HYBRID)

    scaling_mod_size = 30
    first_mod_size = 60

    parameters.SetScalingModSize(scaling_mod_size)
    parameters.SetFirstModSize(first_mod_size)

    mult_depth = 7

    parameters.SetMultiplicativeDepth(mult_depth)
    cc = GenCryptoContext(parameters)
    cc.Enable(PKESchemeFeature.PKE)
    cc.Enable(PKESchemeFeature.KEYSWITCH)
    cc.Enable(PKESchemeFeature.LEVELEDSHE)
    cc.Enable(PKESchemeFeature.ADVANCEDSHE)

    key_pair = cc.KeyGen()
    cc.EvalMultKeyGen(key_pair.secretKey)
    cc.EvalSumKeyGen(key_pair.secretKey);

    cc_bin = Serialize(cc, BINARY)
    sk_bin = Serialize(key_pair.secretKey, BINARY)
    pk_bin = Serialize(key_pair.publicKey, BINARY)
    
    os.makedirs(PUB_KEY_DIR, exist_ok=True)
    cc.SerializeEvalMultKey(os.path.join(PUB_KEY_DIR,f'mk-{key_id}.bin'), BINARY)
    cc.SerializeEvalAutomorphismKey(os.path.join(PUB_KEY_DIR,f'ak-{key_id}.bin'), BINARY)
    return cc_bin, sk_bin, pk_bin

def fhe_encrypt(vec: List[float], cc_b, public_key_b):
     cc = DeserializeCryptoContextString(cc_b, BINARY)
     if cc is None:
        raise Exception("DeserializeCryptoContext error")
     public_key = DeserializePublicKeyString(public_key_b, BINARY)
     if public_key is None:
        raise Exception("DeserializePublicKey error")

     c_vec = [complex(a,0) for a in vec] 
     plaintext = cc.MakeCKKSPackedPlaintext(c_vec)
     ciphertext = cc.Encrypt(public_key, plaintext)
     b = Serialize(ciphertext, BINARY )
     return b

def prune_pub_key_dir(ids: List[str]):
    os.makedirs(PUB_KEY_DIR, exist_ok=True)
    cnt = 0
    for filename in os.listdir(PUB_KEY_DIR):
        file_path = os.path.join(PUB_KEY_DIR, filename)
        if not any(id in filename for id in ids):
            os.remove(file_path)
            print(f"Removed file: {file_path}")
            cnt += 1
    return cnt


