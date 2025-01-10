{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
  };
  outputs = {self, nixpkgs}@inputs: let
    forAllSys = nixpkgs.lib.genAttrs nixpkgs.lib.platforms.all;
    APPNAME = "yt-playlist-dl";
    program = {
      APPNAME
      , lib
      , writeShellScriptBin
      , yt-dlp
      , src-pyenv
      , ...
    }: writeShellScriptBin APPNAME ''
      export PATH=$PATH:${lib.makeBinPath [ yt-dlp ]}
      exec ${src-pyenv.interpreter} ${./main.py} "$@"
    '';
  in {
    overlays = {
      default = final: prev: {
        ${APPNAME} = prev.callPackage program ({
          inherit APPNAME;
        } // inputs);
      };
      pyenv = final: prev: {
        src-pyenv = prev.python3.withPackages (ps: [ ps.beautifulsoup4 ps.ffmpeg-python ]);
      };
    };
    packages = forAllSys (system: let
      pkgs = import nixpkgs { inherit system; overlays = [ self.overlays.pyenv self.overlays.default ]; };
    in {
      default = pkgs.${APPNAME};
      ${APPNAME} = pkgs.${APPNAME};
    });
    devShells = forAllSys (system: let
      pkgs = import nixpkgs { inherit system; overlays = [ self.overlays.pyenv ]; };
    in {
      default = pkgs.mkShell {
        name = "${APPNAME}-env";
        packages = with pkgs; [ src-pyenv yt-dlg ];
      };
    });
  };
}
