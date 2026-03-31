{
  description = "rep-log — Python + React development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      pythonEnv = pkgs.python313.withPackages (ps:
        with ps; [
          fastapi
          uvicorn
          uvloop
          httptools
          websockets
          watchfiles
          python-dotenv

          sqlalchemy
          alembic
          asyncpg
          greenlet
          pydantic-settings

          passlib
          bcrypt
          python-jose
          email-validator
          python-multipart

          pytest
          pytest-cov
          pytest-asyncio
          httpx
          ruff
          mypy
          ipython
        ]);
    in {
      devShells.default = pkgs.mkShell {
        packages = [
          pythonEnv
          pkgs.pre-commit
          pkgs.git
          pkgs.just
          pkgs.ripgrep
          pkgs.fd

          # frontend
          pkgs.nodejs_22
          pkgs.nodePackages.npm
        ];

        shellHook = ''
          export PYTHONPATH="$PWD/src:$PYTHONPATH"

          echo

          if [ -f .pre-commit-config.yaml ]; then
            pre-commit install >/dev/null 2>&1 || true
          fi

          echo "Commands:"
          echo "  just test                    run tests"
          echo "  just cov                     coverage"
          echo "  just lint                    lint"
          echo "  just fmt                     format"
          echo "  just check                   type check"
          echo "  just run                     run the app"
          echo "  just migrate \"description\"   generate a migration"
          echo "  just upgrade                 apply migrations"
          echo "  just downgrade               roll back one step"
          echo "  just db-drop                 delete the local database"
          echo "  just fe                      run frontend dev server"
          echo "  just fe-build                build frontend"
          echo
        '';
      };
    });
}
