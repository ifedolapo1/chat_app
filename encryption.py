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
print('UserAPubKey : ', userAPubKey)
print('------------------------\n')

userBPrivKey = secrets.randbelow(ec_curve.field.n)
userBPubKey = userBPrivKey * ec_curve.g

print('------------------------')
print('UserAPubKey : ', userBPubKey)
print('------------------------\n')


def AES_GCM_encrypt(message, secretKey):
    aesCipher = AES.new(secretKey, AES.MODE_GCM)
    ciphertext, authTag = aesCipher.encrypt_and_digest(message)
    return (ciphertext, aesCipher.nonce, authTag)


def AES_GCM_decrypt(ciphertext, nonce, authTag, secretKey):
    aesCipher = AES.new(secretKey, AES.MODE_GCM, nonce)
    plaintext = aesCipher.decrypt_and_verify(ciphertext, authTag)
    return plaintext


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
