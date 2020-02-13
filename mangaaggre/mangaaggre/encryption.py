from Crypto.Cipher import AES
import base64

def decrypt(encrypted) -> str:
    encrypted = base64.b64decode(encrypted)
    passphrase = "123456781234567G"
    iv = "ABCDEF1G34123412"
    aes = AES.new(passphrase, AES.MODE_CBC, iv)

    decrypted = aes.decrypt(encrypted)
    return decrypted.strip().decode('utf8')