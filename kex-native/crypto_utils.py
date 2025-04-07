import oqs
import nacl.public
import liboqs

def generate_ecdh_keypair():
    private_key = nacl.public.PrivateKey.generate()
    public_key = private_key.public_key
    return private_key, public_key

def generate_kyber_keypair(variant = "Kyber768"):
    kem = oqs.KeyEncapsulation(variant)
    public_key = kem.generate_keypair()
    return kem, public_key

def derive_ecdh_shared_secret(my_private_key, their_public_key):
    box = nacl.public.Box(my_private_key, their_public_key)
    return box.shared_key()

def derive_kyber_shared_secret(kem, ciphertext):
    return kem.decap_secret(ciphertext)

def create_hybrid_secret(secret1: bytes, secret2: bytes) -> bytes:
    return secret1 + secret2