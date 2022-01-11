#!flask/bin/python
# -*- coding: utf-8 -*-

import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES

import utils.configuration

def hash_password(password):

    configuration = utils.configuration.load()

    password = password.encode('utf-8')
    salt = (configuration['DEFAULT']['SECRET_KEY']).encode('utf-8')

    return hashlib.sha256(password + salt).hexdigest()


class AESCipher(object):

    def __init__(self, key):
        self.block_size = 64
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(
            enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.block_size - len(s) % self.block_size) * \
            chr(self.block_size - len(s) % self.block_size)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]
