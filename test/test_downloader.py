from pathlib import Path
from typing import Callable, Iterator, Optional
from unittest.mock import MagicMock, PropertyMock, patch

from requests.models import Response

from astro_pi_executor.downloader import Downloader, url_prefix
from test_utils import get_test_resource


def fake_get(substituter: Optional[Callable[[str], str]]):
    def _fake_get(url: str, stream: bool, timeout: int) -> Response:
        url = url.replace(url_prefix, "")
        if url.startswith("/") and len(url) > 1:
            # remove leading slash
            url = url[1:]
        if substituter is not None:
            url = substituter(url)
        response = MagicMock(spec=Response)
        try:
            requested_file: Path = get_test_resource(url)
            type(response).status_code = PropertyMock(return_value=200)
            with requested_file.open("rb") as f:
                content: bytes = f.read()
                headers = {"content-length": str(len(content))}
                response.return_value = response
                response.return_value.__enter__.return_value = response
                type(response).headers = PropertyMock(return_value=headers)

                def fake_iter_content(
                    chunk_size: Optional[int] = None, decode_unicode: bool = False
                ) -> Iterator[bytes]:
                    final_chunk_size: int = 1024 if chunk_size is None else chunk_size
                    i: int = 0
                    while i <= len(content):
                        upper_bound: int = i + final_chunk_size
                        if upper_bound >= len(content):
                            yield content[i : len(content)]
                            break
                        else:
                            yield content[i:upper_bound]
                            i += final_chunk_size

            response.iter_content.side_effect = fake_iter_content

        except FileNotFoundError:
            type(response).status_code = PropertyMock(return_value=400)
        return response

    return _fake_get


def test_downloader_should_download_and_install_data(tmp_path: Path):
    downloader = Downloader()
    with patch("astro_pi_executor.downloader.requests") as mock_requests:
        mock_requests.get.side_effect = fake_get(
            lambda x: x.replace("OrbitAz", "TestDownload")
        )
        downloader.download(tmp_path)

    assert (tmp_path / "OrbitAz.zip").exists()

    downloader.install(tmp_path)
    name = "AstroPi_2021_colour.png"
    assert (tmp_path / name).exists()


# TODO this is an integration test
def test_downloader_when_no_sha256_installed_skips():
    pass


# TODO this is an integration test
def test_downloader_when_no_gpg_installed_skips():
    pass
