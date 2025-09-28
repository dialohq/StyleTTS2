{
  description = "ZERO VAD";
  nixConfig = {
    extra-substituters = ["https://nix-community.cachix.org"];
    extra-trusted-public-keys = [
      "nix-community.cachix.org-1:mB9FSh9qf2dCimDSUo8Zy7bkq5CX+/rkCWyvRCYg3Fs="
    ];
  };
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    nix-gl-host.url = "github:numtide/nix-gl-host";
    nix-gl-host.inputs.nixpkgs.follows = "nixpkgs";
  };
  outputs = {
    nixpkgs,
    flake-utils,
    nix-gl-host,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {
        inherit system;
        config.allowUnfree = true;
        config.cudaSupport = true;
      };
    in {
      devShells.default = pkgs.mkShell {
        packages = with pkgs;
          [
            python311
            uv
            alejandra
            protobuf
            portaudio
            espeak-ng
            yq-go
            dyff
          ]
          ++ (
            if pkgs.stdenv.isLinux
            then [
              nix-gl-host.defaultPackage.${system}
            ]
            else []
          );
        "LD_LIBRARY_PATH" = pkgs.lib.makeLibraryPath (with pkgs;
          [
          ]
          ++ (
            if pkgs.stdenv.isLinux
            then [
              cudaPackages_12_1.backendStdenv.cc.cc.lib
            ]
            else []
          ));
        shellHook =
          if pkgs.stdenv.isLinux
          then ''
            export LD_LIBRARY_PATH=$(${nix-gl-host.defaultPackage.${system}}/bin/nixglhost -p):${
              pkgs.lib.makeLibraryPath [
                pkgs.espeak-ng
              ]
            }:$LD_LIBRARY_PATH
            # Set LIBRARY_PATH to help the linker find the CUDA static libraries
            export LIBRARY_PATH=${
              pkgs.lib.makeLibraryPath [
                pkgs.portaudio
                pkgs.espeak-ng
              ]
            }:$LIBRARY_PATH
          ''
          else ''
            export DYLD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [pkgs.portaudio pkgs.espeak-ng]}:$DYLD_LIBRARY_PATH"
          '';
      };
    });
}

