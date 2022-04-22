import base64
from tinyec import registry
from Crypto.Cipher import AES
import hashlib
import secrets
import binascii

# Get Elliptic curve using brainpoolP256r1
ec_curve = registry.get_curve('brainpoolP256r1')

userAPrivKey = secrets.randbelow(ec_curve.field.n)
userAPubKey = userAPrivKey * ec_curve.g

print('------------------------')
print('UserAPrivKey : ', userAPrivKey)
print('------------------------\n')

print('------------------------')
print('UserAPubKey : ', userAPubKey)
print('------------------------\n')

print('------------------------')
print('UserAPubKey : ', userAPrivKey * ec_curve.g)
print('------------------------\n')

userBPrivKey = secrets.randbelow(ec_curve.field.n)
userBPubKey = userBPrivKey * ec_curve.g

print('------------------------')
print('userBPrivKey : ', userBPrivKey)
print('------------------------\n')

print('------------------------')
print('UserBPubKey : ', userBPubKey)
print('------------------------\n')

def generateUserPrivateKey():
    userPrivKey = secrets.randbelow(ec_curve.field.n)
    return userPrivKey

def generateUserPublicKey():
    userPubKey = userAPrivKey * ec_curve.g
    return userPubKey

def AES_GCM_encrypt(message, secretKey):
    aesCipher = AES.new(secretKey, AES.MODE_GCM)
    ciphertext, authTag = aesCipher.encrypt_and_digest(message)
    return (ciphertext, aesCipher.nonce, authTag)


def AES_GCM_decrypt(ciphertext, nonce, authTag, secretKey):
    aesCipher = AES.new(secretKey, AES.MODE_GCM, nonce)
    plaintext = aesCipher.decrypt_and_verify(ciphertext, authTag)
    return plaintext

""" def encrypt_privkey(private_key, secure_pass):
    secure_private_key = base64.b64encode(AES.new(secure_pass, AES.MODE_GCM).encrypt(private_key))
    print('Encrypt private key: ', secure_private_key)
    return secure_private_key

def decrypt_privkey(private_key, secure_pass):
    original_private_key = base64.b64decode(AES.new(secure_pass, AES.MODE_GCM).encrypt(private_key))
    print('Decrypt private key: ', original_private_key)
    return original_private_key """

def ecc_point_to_256_bitkey(point):
    sha = hashlib.sha256(int.to_bytes(point.x, 32, 'big'))
    sha.update(int.to_bytes(point.x, 32, 'big'))
    return sha.digest()


def ECC_encrypt(message, pubKey, privKey):
    ECCSharedKey = privKey * pubKey
    secretKey = ecc_point_to_256_bitkey(ECCSharedKey)
    ciphertext, nonce, authTag = AES_GCM_encrypt(message, secretKey)
    ciphertextPubKey = privKey * ec_curve.g
    return (ciphertext, nonce, authTag, ciphertextPubKey)


def ECC_decrypt(encryptedMessage, privKey):
    (ciphertext, nonce, authTag, ciphertextPubKey) = encryptedMessage
    ECCSharedKey = privKey * ciphertextPubKey
    secretKey = ecc_point_to_256_bitkey(ECCSharedKey)
    plaintext = AES_GCM_decrypt(ciphertext, nonce, authTag, secretKey)
    return plaintext

""" h = encrypt_privkey(str(userAPrivKey), 'hello')
decrypt_privkey(str(h), 'hello') """


message = b'hello, how are you doing?'
userAEMessage = ECC_encrypt(message, userBPubKey, userAPrivKey)

print('------------------------')
print('User A encrypted message : ', binascii.hexlify(userAEMessage[0]))
print('------------------------\n')

userBDMessage = ECC_decrypt(userAEMessage, userBPrivKey)

print('------------------------')
print('User B decrypted message : ', userBDMessage)
print('------------------------\n')

message = b'I\'m good, what about you?'
userBEMessage = ECC_encrypt(message, userAPubKey, userBPrivKey)

print('------------------------')
print('User B encrypted message : ', binascii.hexlify(userBEMessage[0]))
print('------------------------\n')

userADMessage = ECC_decrypt(userBEMessage, userAPrivKey)

print('------------------------')
print('User A decrypted message : ', userADMessage)
print('------------------------\n')

print('------------------------')
print('Elliptic Curve Generator : ', ec_curve.g)
print('------------------------\n')
