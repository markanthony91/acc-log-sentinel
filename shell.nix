{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  packages = with pkgs; [
    go
    python311
    python311Packages.pip
    python311Packages.virtualenv
    python311Packages.setuptools
    python311Packages.wheel
    gcc
    pkg-config
    git
  ];

  shellHook = ''
    export PIP_DISABLE_PIP_VERSION_CHECK=1
    export GOCACHE=/tmp/acc_log_sentinel-gocache
    export GOMODCACHE=/tmp/acc_log_sentinel-gomodcache
    echo "acc_log_sentinel nix-shell ativo"
    echo "Go cache: $GOCACHE"
    echo "Go mod cache: $GOMODCACHE"
  '';
}
