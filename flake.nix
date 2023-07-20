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
        pythonVersionDerivation = pkgs.runCommand "pythonVersion" {
          src = builtins.path { path = ./.; inherit name; };
          gnumake = pkgs.gnumake;
        } ''
          cd $src
          $gnumake/bin/make python_version > $out
        '';
        pythonVersion = builtins.readFile pythonVersionDerivation;

        pythonVersionNixName = pkgs.lib.strings.removeSuffix "\n" (
          builtins.replaceStrings ["."] [""] pythonVersion);
        pythonPkgs = builtins.getAttr ("python" + pythonVersionNixName + "Packages") pkgs;
        venvDir = "venv";
      in {
        packages.pythonVersion = pythonVersion;
        devShells.default = pkgs.makeOverridable pkgs.mkShell {
          name = "impurePythonVenv";
          inherit venvDir;

          buildInputs = [
            pkgs.coreutils
            pkgs.docker
            pkgs.findutils
            pkgs.git
            pkgs.gnugrep
            pkgs.gnumake
            pkgs.gnused
            pkgs.ffmpeg

            pythonPkgs.python
            pythonPkgs.tkinter
            pythonPkgs.venvShellHook

          ];

          postVenvCreation = ''
            unset SOURCE_DATE_EPOCH
            ln -s ${pythonPkgs.tkinter}/lib/python*/site-packages/_tkinter.cpython-*-*.so venv/lib/python*/site-packages/
            pip install -r requirements.txt
            pip install -r requirements-dev.txt
          '';

          postShellHook = ''
            unset SOURCE_DATE_EPOCH
          '';
        };
      });
}
