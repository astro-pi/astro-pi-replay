{
  inputs = {
    # Package sets
    nixpkgs.url = github:nixos/nixpkgs/nixpkgs-unstable;
    flake-utils.url = github:numtide/flake-utils;
  };

  outputs = { self, nixpkgs, flake-utils, ... }@inputs:
    flake-utils.lib.eachDefaultSystem (system:
      let
        name = "astro_pi_executor";
        pkgs = nixpkgs.legacyPackages.${system};
        # Version specified in pyproject.toml
        pythonVersion = pkgs.lib.strings.removeSuffix "\n" (
          builtins.replaceStrings ["."] [""] (
            builtins.readFile (pkgs.runCommand "pythonVersion" {
              src = builtins.path { path = ./.; inherit name; };
              gnumake = pkgs.gnumake;
            } ''
              cd $src
              $gnumake/bin/make python_version > $out
              '')
          )
        );
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pkgs.coreutils
            pkgs.docker
            pkgs.findutils
            pkgs.git
            pkgs.gnugrep
            pkgs.gnumake
            pkgs.gnused
            # Dynamically fetch the python version from pyproject.toml
            (builtins.getAttr ("python" + builtins.replaceStrings ["."] [""] pythonVersion) pkgs)
          ];
        };
      });
}
