{
  description = "Python builds for thesis benchmarking";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };

      cflags = [ "-mtune=native" "-march=native" ];
      opts = {
        enableOptimizations = true;
        enableLTO = true;
        reproducibleBuild = false;
      };

      python311 = (pkgs.python311.overrideAttrs (oldAttrs: rec {
        CFLAGS = oldAttrs.CFLAGS or [] ++ cflags;
      })).override opts;

      python313 = (pkgs.python313.overrideAttrs (oldAttrs: rec {
        CFLAGS = oldAttrs.CFLAGS or [] ++ cflags;
      })).override opts;

      # python313_JIT = (pkgs.python313.overrideAttrs (oldAttrs: rec {
      #   CFLAGS = oldAttrs.CFLAGS or [] ++ cflags;
      #   configureFlags = oldAttrs.configureFlags or [] ++ [ "--enable-experimental-jit" ];
      #   buildInputs = oldAttrs.buildInputs or [] ++ [ pkgs.llvm_18 ];
      #   nativeBuildInputs = oldAttrs.nativeBuildInputs or [] ++ [ pkgs.clang_18 ]; # [ pkgs.breakpointHook ];
      # })).override opts;

      flint = (pkgs.flint3.overrideAttrs (oldAttrs: rec {
        CFLAGS = oldAttrs.CFLAGS or [] ++ cflags;
        configureFlags = oldAttrs.configureFlags or [] ++ [ "--enable-avx2" ];
      }));
    in
      {
        packages.${system} = {
          # inherit python311 python313 python313_JIT;
          inherit python311 python313;
        };

        devShells.${system}.default = pkgs.mkShell {
          packages = [
            python311
            python311.pkgs.pip

            python313
            python313.pkgs.pip

            # python313_JIT
            # python313_JIT.pkgs.pip

            flint
          ];

          inputsFrom = [ flint ];

          # shellHook = ''
          #   alias python313-JIT=${python313_JIT}/bin/python3;
          # '';

          shellHook = ''
            export PYTHON311_VENV=.venv-311
            export PYTHON313_VENV=.venv-313

            if test ! -d $PYTHON311_VENV; then
              python3.11 -m venv $PYTHON311_VENV
            fi

            if test ! -d $PYTHON313_VENV; then
              python3.13 -m venv $PYTHON313_VENV
            fi

            . .venv-311/bin/activate .venv-311/
          '';

        };
      };
}
