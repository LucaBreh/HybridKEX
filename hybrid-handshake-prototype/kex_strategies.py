import oqs
from nacl.public import PrivateKey, PublicKey, Box

class ClassicKEX:
    def __init__(self, algorithm="x25519"):
        if algorithm.lower() != "x25519":
            raise ValueError(f"Unsupported classic algorithm: {algorithm}")
        self.private_key = PrivateKey.generate()
        self.public_key = self.private_key.public_key

    def generate_keys(self):
        priv = self.private_key
        pub = bytes(self.public_key)
        return priv, pub

    def compute_shared_secret(self, peer_public_key_bytes: bytes) -> bytes:
        peer_pubkey = PublicKey(peer_public_key_bytes)
        box = Box(self.private_key, peer_pubkey)
        return box.shared_key()


class PQCKEX:
    def __init__(self, kem_alg="Kyber768"):
        self.kem_alg = kem_alg
        self.kem = None
        self.public_key = None

    def generate_keys(self):
        self.kem = oqs.KeyEncapsulation(self.kem_alg)
        self.public_key = self.kem.generate_keypair()
        return self.kem, self.public_key

    def compute_shared_secret(self, ciphertext):
        return self.kem.decap_secret(ciphertext)


class HybridKEX:
    def __init__(self, classic_alg="x25519", pqc_alg="Kyber768"):
        self.classic = ClassicKEX(classic_alg)
        self.pqc = PQCKEX(pqc_alg)
        self.hybrid_key = None
        self.classic_pub = None
        self.pqc_pub = None

    def generate_keys(self):
        _, self.classic_pub = self.classic.generate_keys()
        self.pqc_kem, self.pqc_pub = self.pqc.generate_keys()
        return self.classic_pub, self.pqc_pub

    def compute_shared_secret(self, classic_peer_pub, pqc_ciphertext):
        classic_shared = self.classic.compute_shared_secret(classic_peer_pub)
        pqc_shared = self.pqc.compute_shared_secret(pqc_ciphertext)
        self.hybrid_key = classic_shared + pqc_shared
        return self.hybrid_key


