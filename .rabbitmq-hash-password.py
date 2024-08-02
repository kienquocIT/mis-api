#!/usr/bin/env python3
import base64
import os
import hashlib
import sys

if __name__ == '__main__':
    for password in sys.argv:
        salt = os.urandom(4)
        tmp0 = salt + password.encode('utf-8')
        tmp1 = hashlib.sha256(tmp0).digest()
        salted_hash = salt + tmp1
        pass_hash = base64.b64encode(salted_hash)
        print(password, ':', pass_hash.decode("utf-8"))
