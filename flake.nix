{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
  };
  outputs = {self, nixpkgs}@inputs: let
    forAllSys = nixpkgs.lib.genAttrs nixpkgs.lib.platforms.all;
    APPNAME = "dlvids";
    program = {
      APPNAME
      , lib
      , writeShellScriptBin
      , yt-dlp
      , pyenv
      , ...
    }: writeShellScriptBin APPNAME ''
      export PATH=$PATH:${lib.makeBinPath [ yt-dlp ]}
      exec ${pyenv.interpreter} ./main.py "$@"
    '';
  in {
    overlays = {
      default = final: prev: {
        ${APPNAME} = prev.callPackage program ({
          inherit APPNAME;
          pyenv = prev.python3.withPackages (ps: [ ps.beautifulsoup4 ps.ffmpeg-python ]);
        } // inputs);
      };
    };
    packages = forAllSys (system: let
      pkgs = import nixpkgs { inherit system; overlays = [ self.overlays.default ]; };
    in {
      default = pkgs.${APPNAME};
      ${APPNAME} = pkgs.${APPNAME};
    });
    devShells = forAllSys (system: let
      pkgs = import nixpkgs { inherit system; };
      pyenv = pkgs.python3.withPackages (ps: [ ps.beautifulsoup4 ps.ffmpeg-python ]);
    in {
      default = pkgs.mkShell {
        name = "${APPNAME}-env";
        packages = with pkgs; [ pyenv yt-dlg ];
      };
    });
  };
}
