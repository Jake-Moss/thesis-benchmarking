{
  description = "Python builds for thesis benchmarking";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };

      cflags = [ "-g" "-mtune=native" "-march=native" "-fno-omit-frame-pointer" "-mno-omit-leaf-frame-pointer" ];
      opts = {
        enableOptimizations = true;
        enableLTO = true;
        reproducibleBuild = false;
      };

      py312 = (pkgs.python312.overrideAttrs (oldAttrs: rec {
        CFLAGS = oldAttrs.CFLAGS or [] ++ cflags;
        dontStrip = true;
      })).override opts;

      py313 = (pkgs.python313.overrideAttrs (oldAttrs: rec {
        CFLAGS = oldAttrs.CFLAGS or [] ++ cflags;
        dontStrip = true;
      })).override opts;

      py313_JIT = (pkgs.python313.overrideAttrs (oldAttrs: rec {
        CFLAGS = oldAttrs.CFLAGS or [] ++ cflags;
        dontStrip = true;
        configureFlags = oldAttrs.configureFlags or [] ++ [ "--enable-experimental-jit" ];
        buildInputs = oldAttrs.buildInputs or [] ++ [ pkgs.llvm_18 ];
        nativeBuildInputs = oldAttrs.nativeBuildInputs or [] ++ [ pkgs.clang_18 ];
      })).override opts;

      flint = (pkgs.flint3.overrideAttrs (oldAttrs: rec {
        CFLAGS = oldAttrs.CFLAGS or [] ++ cflags;
        dontStrip = true;
        configureFlags = oldAttrs.configureFlags or [] ++ [ "--enable-avx2" ];
      }));
    in
      {
        devShells.${system}.default = pkgs.mkShell {
          packages = [
            (py312.withPackages (python-pkgs: [
              python-pkgs.python-lsp-server
              python-pkgs.python-lsp-ruff
              python-pkgs.matplotlib
              python-pkgs.pygobject3
              python-pkgs.pandas
              python-pkgs.sympy
              python-pkgs.seaborn
            ]))
            pkgs.memray

            pkgs.ruff

            py312
            py312.pkgs.pip

            py313
            py313.pkgs.pip

            # py313_JIT
            # py313_JIT.pkgs.pip

            flint
            pkgs.pkg-config
            pkgs.ninja

            pkgs.samply
            pkgs.libz
            pkgs.lz4
            pkgs.libunwind
            pkgs.nixseparatedebuginfod
            pkgs.elfutils
          ];

          inputsFrom = [ flint ];
          buildInputs = [ flint ];

          # postShellHook = ''
          #   alias py313-JIT=${py313_JIT}/bin/python3;
          # '';

          postShellHook = ''
            unset SOURCE_DATE_EPOCH
            . init-venvs.sh
            export SYMPY_GROUND_TYPES=python
          '';

          LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [ pkgs.stdenv.cc.cc pkgs.libz ];
          NIX_DEBUG_INFO_DIRS = "${py312.debug}/lib/debug:${py313.debug}/lib/debug";

        };
      };
}
