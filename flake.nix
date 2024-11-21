{
  description = "Container Packing";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.devshell.url = "github:numtide/devshell";

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    devshell,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {
        inherit system;
        config.allowUnfree = true;
        overlays = [devshell.overlays.default];
      };

      myPython = pkgs.python312.withPackages (p:
        with p; [
          # Basic
          rich

          matplotlib
          numpy
          ezdxf
        ]);
    in {
      devShell = pkgs.devshell.mkShell {
        name = "Formula10";

        packages = with pkgs; [
          myPython
        ];

        # Use $1 for positional args
        commands = [];
      };
    });
}
