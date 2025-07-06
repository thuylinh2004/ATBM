from Crypto.PublicKey import RSA

def load_key(filename):
    with open(filename, 'rb') as f:
        return RSA.import_key(f.read())

receiver_private = load_key('receiver_private.pem')
receiver_public = load_key('receiver_public.pem')
sender_private = load_key('sender_private.pem')
sender_public = load_key('sender_public.pem')