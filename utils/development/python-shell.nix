{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    (pkgs.python3.withPackages (ps: [
      ps.cryptography
    ]))
  ];

  shellHook = ''
    echo "Generating encryption keys..."
    echo "AES_KEY: $(python3 -c 'import os, base64; print(base64.urlsafe_b64encode(os.urandom(32)).decode())')"
    echo "ENCRYPTION_KEY: $(python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
    echo "Copy these keys to your .env file"
  '';
}
