FROM ghcr.io/astral-sh/uv:0.9.8 AS uv


FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

COPY --from=uv /uv /uvx /bin/

WORKDIR /usr/src/app

COPY . .

RUN uv sync --locked --extra app

EXPOSE 9080

CMD [ "uv", "run", "granian", "--interface", "asginl", "src/yt_dlp_restate.run:app", "--host", "0.0.0.0", "--port", "9080" ]
