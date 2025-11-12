from typing import Any

import obstore
import restate
from pydantic import Field
from pydantic_settings import BaseSettings

from yt_dlp_restate import create_service


class Settings(BaseSettings):
    object_store_url: str
    youtube_params: dict[str, Any] | None = None  # pyright: ignore[reportExplicitAny]
    identity_keys: list[str] = Field(alias="restate_identity_keys", default=[])


settings = Settings()  # pyright: ignore[reportCallIssue]

object_store = obstore.store.from_url(settings.object_store_url)
service = create_service(object_store, base_params=settings.youtube_params)

app = restate.app(services=[service], identity_keys=settings.identity_keys)
