{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python312
    pkgs.uv
    pkgs.git
    (pkgs.python312.withPackages (ps: [
      ps.cryptography
      ps.pip
      ps.setuptools
    ]))
  ];

  shellHook = ''
    echo "Setting up Codegen MCP Server environment..."
    echo "Environment ready for Codegen MCP Server installation"
  '';
}
