{
  description = "Python builds for thesis benchmarking";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };

      cflags = [ "-mtune=native" "-march=native" "-fno-omit-frame-pointer" "-mno-omit-leaf-frame-pointer" ];
      opts = {
        enableOptimizations = true;
        enableLTO = true;
        reproducibleBuild = false;
      };

      py312 = (pkgs.python312.overrideAttrs (oldAttrs: rec {
        CFLAGS = oldAttrs.CFLAGS or [] ++ cflags;
      })).override (opts // {
        packageOverrides = python-final: python-prev: {
          sympy = python-prev.sympy.overridePythonAttrs (oldAttrs: rec {
            version = "1.13.2";
            src = python-final.fetchPypi {
              pname = "sympy";
              inherit version;
              sha256 = "401449d84d07be9d0c7a46a64bd54fe097667d5e7181bfe67ec777be9e01cb13";
            };
          });
        };
      });

      py313 = (pkgs.python313.overrideAttrs (oldAttrs: rec {
        CFLAGS = oldAttrs.CFLAGS or [] ++ cflags;
      })).override opts;

      # py313_JIT = (pkgs.python313.overrideAttrs (oldAttrs: rec {
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
        # packages.${system} = {
        #   # inherit py312 py313 py313_JIT;
        #   inherit py312 py313;
        # };

        devShells.${system}.default = pkgs.mkShell {
          packages = [
            (py312.withPackages (python-pkgs: [
              python-pkgs.python-lsp-server
              python-pkgs.python-lsp-ruff
              python-pkgs.matplotlib
              python-pkgs.pygobject3
              python-pkgs.pandas
              python-pkgs.sympy
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

            pkgs.linuxKernel.packages.linux_6_10.perf
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
        };
      };
}
