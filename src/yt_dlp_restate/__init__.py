from __future__ import annotations

import logging
import os
import posixpath
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, final

import obstore
import restate
import yt_dlp
from pydantic import BaseModel

if TYPE_CHECKING:
    from yt_dlp import _Params  # pyright: ignore[reportPrivateUsage]

logger = logging.getLogger(__name__)


class DownloadRequest(BaseModel):
    """Request for downloading a video using yt-dlp."""

    url: str
    prefix: str = ""


@final
class Downloader:
    """
    Downloader for videos using yt-dlp.
    """

    def __init__(
        self,
        store: obstore.store.ObjectStore,
        base_params: _Params | None = None,
        logger: logging.Logger = logger,
    ):
        self.store = store
        self.base_params: _Params = base_params.copy() if base_params else {}
        self.logger = logger

    @final
    def download(self, request: DownloadRequest):
        self.logger.info("Downloading video", extra={"url": request.url})

        params = self.base_params.copy()

        # Join with fake root and normalize
        prefix = (
            posixpath.normpath(posixpath.join("/__root", request.prefix))
            .removeprefix("/__root/")
            .removeprefix("/__root")
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            params["paths"] = {"home": temp_dir}  # pyright: ignore[reportGeneralTypeIssues]

            with yt_dlp.YoutubeDL(params) as ydl:
                ydl.download([request.url])

            for file in os.listdir(temp_dir):
                logger.info("Uploading file", extra={"file": file})

                _ = self.store.put(
                    posixpath.join(prefix, file),
                    Path(os.path.join(temp_dir, file)),
                )


def create_service(
    store: obstore.store.ObjectStore,
    base_params: _Params | None = None,
    service_name: str = "YoutubeDownloader",
) -> restate.Service:
    """
    Create a service for downloading videos using yt-dlp.

    Args:
        store: The object store to use for storing downloaded videos.
        base_params: The base parameters to use for yt-dlp.
        service_name: The name of the service.

    Returns:
        The created service.
    """
    service = restate.Service(service_name)

    downloader = Downloader(store, base_params)

    @service.handler()  # pyright: ignore [reportUnknownMemberType, reportUntypedFunctionDecorator]
    async def download(  # pyright: ignore [reportUnusedFunction]
        ctx: restate.Context,
        request: DownloadRequest,
    ):
        _ = await ctx.run_typed("download", downloader.download, request=request)

    return service
