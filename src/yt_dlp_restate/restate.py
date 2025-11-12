from __future__ import annotations

from typing import TYPE_CHECKING

import obstore
import restate
from .downloader import Downloader, DownloadRequest, DownloaderOptions

if TYPE_CHECKING:
    from yt_dlp import _Params  # pyright: ignore[reportPrivateUsage]


def create_service(
    store: obstore.store.ObjectStore,
    base_params: _Params | None = None,
    options: DownloaderOptions | None = None,
    service_name: str = "YoutubeDownloader",
) -> restate.Service:
    """
    Create a service for downloading videos using yt-dlp.

    Args:
        store: The object store to use for storing downloaded videos.
        base_params: The base parameters to use for yt-dlp.
        file_filter: The file filter to use for filtering uploaded files.
        service_name: The name of the service.

    Returns:
        The created service.
    """
    service = restate.Service(service_name)

    downloader = Downloader(store, base_params, options)

    @service.handler()  # pyright: ignore [reportUnknownMemberType, reportUntypedFunctionDecorator]
    async def download(  # pyright: ignore [reportUnusedFunction]
        ctx: restate.Context,
        request: DownloadRequest,
    ):
        _ = await ctx.run_typed("download", downloader.download, request=request)

    return service
