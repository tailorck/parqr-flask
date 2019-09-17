"""
This module creates a key pair to encrypt your Piazza username and password.
The scraper with read the .login file created and decrypt the username and
password with the private key saved as .key.pem
"""
from Crypto.PublicKey import RSA
from Crypto import Random
import getpass
import os

random_generator = Random.new().read
key = RSA.generate(1024, random_generator)
public_key = key.publickey()
seed = 42

email = input("Email: ")
password = getpass.getpass()

curr_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(curr_dir, '.login'), 'w') as f:
	# encrypt method does not support encrypting a string message.
	# Try encoding your string to bytes first using encode
    f.write(str(public_key.encrypt(email.encode('utf-8'), seed)[0]))
    f.write(str(public_key.encrypt(password.encode('utf-8'), seed)[0]))

with open(os.path.join(curr_dir, '.key.pem'), 'w') as f:
	# encrypt performs "textbook" RSA encryption, which is insecure due to the lack of padding.
	# You should instead look to use either Crypto.Cipher.PKCS1_OAEP or Crypto.Cipher.PKCS1_v1_5.
    f.write(str(key.exportKey()))