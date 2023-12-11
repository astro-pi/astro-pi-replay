from pathlib import Path
from typing import Callable, Iterator, Optional
from unittest.mock import MagicMock, PropertyMock, patch

from requests.models import Response

from astro_pi_replay.downloader import (
    SEQUENCES_FILE,
    SEQUENCES_FILENAME,
    Downloader,
    url_prefix,
    version_url_prefix,
)
from test_utils import get_test_resource


# Helper methods for mocking requests library
def response_404() -> Response:
    response = MagicMock(spec=Response)
    type(response).status_code = PropertyMock(return_value=404)
    return response


def response_200_for(resource_path: str):
    response = MagicMock(spec=Response)
    type(response).status_code = PropertyMock(return_value=200)
    type(response).content = PropertyMock(
        return_value=get_test_resource(resource_path).read_bytes()
    )
    return response


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


# tests


def test_when_sequence_update_available_should_update(tmp_path: Path):
    downloader: Downloader = Downloader()
    downloaded_sequences_file: Path = tmp_path / "sequences.csv"

    assert downloaded_sequences_file.exists() is False
    with patch("astro_pi_replay.downloader.SEQUENCES_FILE", downloaded_sequences_file):
        # Mock the sequences.csv check response
        with patch("astro_pi_replay.downloader.requests") as mock_requests:
            mocked_response: MagicMock = response_200_for(SEQUENCES_FILENAME)
            mock_requests.get.return_value = mocked_response
            downloader.check_for_sequences_override()
            assert (
                mock_requests.method_calls[0].args[0]
                == f"{version_url_prefix}/{SEQUENCES_FILENAME}"
            )
    assert downloader.checked_for_sequences_override is True
    assert downloaded_sequences_file.exists() is True
    assert downloaded_sequences_file.read_text() == SEQUENCES_FILE.read_text()


def test_when_sequence_update_unavailable_should_ignore(tmp_path: Path):
    downloader: Downloader = Downloader()
    sequences_file: Path = tmp_path / "sequences.csv"
    assert sequences_file.exists() is False

    with patch(
        "astro_pi_replay.downloader.SEQUENCES_FILE", return_value=sequences_file
    ):
        # Mock the sequences.csv check response
        with patch("astro_pi_replay.downloader.requests") as mock_requests:
            mock_requests.get.return_value = response_404()
            downloader.check_for_sequences_override()
            assert (
                mock_requests.method_calls[0].args[0]
                == f"{version_url_prefix}/{SEQUENCES_FILENAME}"
            )
    assert downloader.checked_for_sequences_override is True
    assert sequences_file.exists() is False


def test_downloader_should_download():
    downloader = Downloader()
    name = "replay"
    with patch("astro_pi_replay.downloader.requests") as mock_requests:
        mock_requests.get.side_effect = fake_get(
            # replace the sequence id with TestDownload
            lambda x: x.replace(name, "TestDownload")
        )
        downloader.download(name)
        assert (downloader.tempdir / f"{name}.zip").exists()
        urls = set((call.args[0] for call in mock_requests.method_calls))
        assert f"{url_prefix}/replay.zip.sha256" in urls
        assert f"{url_prefix}/replay.zip.sig" in urls
        assert f"{url_prefix}/replay.zip" in urls


@patch("astro_pi_replay.main.Downloader.has_installed", return_value=False)
def test_downloader_should_download_and_install_data(_, tmp_path: Path):
    name = "replay"
    downloader: Downloader = Downloader()
    downloader.checked_for_sequences_override = True

    with patch("astro_pi_replay.downloader.requests") as mock_requests:
        mock_requests.get.side_effect = fake_get(
            # replace the sequence id with TestDownload
            lambda x: x.replace(name, "TestDownload")
        )
        with patch("astro_pi_replay.downloader.get_replay_dir", return_value=tmp_path):
            downloader.install((1280, 720), "VIS", name)

    vis_dir: Path = tmp_path / "VIS"
    assert vis_dir.exists() and vis_dir.is_dir()
    assert (vis_dir / "AstroPi_2021_colour.png").exists()


# TODO this is an integration test
def test_downloader_when_no_sha256_installed_skips():
    pass


# TODO this is an integration test
def test_downloader_when_no_gpg_installed_skips():
    pass
