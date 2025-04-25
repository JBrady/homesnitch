from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization


def main():
    key_dir = Path(__file__).parent / 'keys'
    key_dir.mkdir(exist_ok=True)

    # Generate EC private key (P-256)
    private_key = ec.generate_private_key(ec.SECP256R1())
    priv_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(key_dir / 'ec_private.pem', 'wb') as f:
        f.write(priv_pem)

    # Generate corresponding public key
    public_key = private_key.public_key()
    pub_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(key_dir / 'ec_public.pem', 'wb') as f:
        f.write(pub_pem)

    print(f"EC key pair generated at {key_dir}")


if __name__ == '__main__':
    main()
