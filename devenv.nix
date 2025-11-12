{ config, pkgs, ... }:

{
  packages = with pkgs; [
    just
    ffmpeg
  ];

  env = {
    OBJECT_STORE_URL = "file://${config.git.root}/var/files";
    GRANIAN_RELOAD_PATHS = "${config.git.root}/src";
  };

  languages = {
    python = {
      enable = true;

      uv.enable = true;
      venv.enable = true;
    };
  };
}
