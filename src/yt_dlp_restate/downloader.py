from __future__ import annotations

import logging
import os
import posixpath
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, final

import obstore
import yt_dlp
from pydantic import BaseModel

if TYPE_CHECKING:
    from yt_dlp import _Params  # pyright: ignore[reportPrivateUsage]

_logger = logging.getLogger(__name__)


class DownloadRequest(BaseModel):
    """Request for downloading a video using yt-dlp."""

    url: str
    prefix: str = ""


@final
class Downloader:
    """
    Downloader for videos using yt-dlp and save them to object storage.
    """

    def __init__(
        self,
        store: obstore.store.ObjectStore,
        base_params: _Params | None = None,  # TODO: expose a custom param object
        logger: logging.Logger = _logger,
    ):
        self.store = store
        self.base_params: _Params = base_params.copy() if base_params else {}
        self.logger = logger

    @final
    def download(self, request: DownloadRequest):
        logger = logging.LoggerAdapter(self.logger, {"url": request.url})

        logger.info("Downloading video")

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

            # Recursively upload all files in the temporary directory
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)

                    # Calculate relative path from temp_dir
                    relative_path = os.path.relpath(file_path, temp_dir)

                    # Convert to posix path for object store key
                    object_key = posixpath.join(
                        prefix, relative_path.replace(os.sep, "/")
                    )

                    logger.info("Uploading file", extra={"file": relative_path})

                    _ = self.store.put(object_key, Path(file_path))
