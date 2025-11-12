[private]
default:
    @just --list

[private]
files:
    @mkdir -p var/files

run: files
    granian --interface asginl src/yt_dlp_restate.run:app --host 0.0.0.0 --port 9080 --reload
