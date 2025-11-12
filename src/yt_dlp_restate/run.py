from typing import Any

import obstore
import restate
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .downloader import DownloaderOptions
from .restate import create_service


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")  # pyright: ignore[reportUnannotatedClassAttribute]

    object_store_url: str
    youtube_params: dict[str, Any] | None = None  # pyright: ignore[reportExplicitAny]
    options: DownloaderOptions = DownloaderOptions()
    identity_keys: list[str] = Field(alias="restate_identity_keys", default=[])


settings = Settings()  # pyright: ignore[reportCallIssue]
# print(settings.model_dump_json())

object_store = obstore.store.from_url(settings.object_store_url)

service = create_service(
    object_store,
    base_params=settings.youtube_params,  # pyright: ignore[reportArgumentType]
    options=settings.options,
)

app = restate.app(services=[service], identity_keys=settings.identity_keys)
