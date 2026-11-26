"""Download and extract the three official archives used by the group project."""

import hashlib
from pathlib import Path
from shutil import copyfileobj
from tempfile import NamedTemporaryFile
from urllib.request import urlopen
from zipfile import BadZipFile, ZipFile
from zlib import crc32


SOURCE = "https://s3.amazonaws.com/tripdata"
ARCHIVES = {
    "JC-202407-citibike-tripdata.csv.zip": "fdd4dd1eadfd87e7bdc47635a31f9c8f4a0e5752f7f8b95f4d8a2fd68617ecab",
    "JC-202408-citibike-tripdata.csv.zip": "ab16afaaaf608b8c2392ff9be547dc77059fd65a990122bad7ebc62e8ad8a141",
    "JC-202409-citibike-tripdata.csv.zip": "9bdf20c1a16ae41b7c4a9f70554166b847703c112e2ddce63d80c6c37ea65ff3",
}
CHUNK_SIZE = 64 * 1024


def verified(path: Path, expected_sha256: str) -> bool:
    if not path.is_file():
        return False
    digest = hashlib.sha256()
    with path.open("rb") as archive:
        for chunk in iter(lambda: archive.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest() == expected_sha256


def download_archive(destination: Path, expected_sha256: str) -> None:
    if verified(destination, expected_sha256):
        print(f"Already verified: {destination.name}")
        return

    url = f"{SOURCE}/{destination.name}"
    with NamedTemporaryFile(dir=destination.parent, suffix=".part", delete=False) as temporary:
        temporary_path = Path(temporary.name)
    try:
        with urlopen(url, timeout=30) as response, temporary_path.open("wb") as archive:
            for chunk in iter(lambda: response.read(CHUNK_SIZE), b""):
                archive.write(chunk)
        if not verified(temporary_path, expected_sha256):
            raise ValueError(f"SHA-256 verification failed for {destination.name}.")
        temporary_path.replace(destination)
        print(f"Downloaded and verified: {destination.name}")
    finally:
        temporary_path.unlink(missing_ok=True)


def matches_csv(path: Path, size: int, expected_crc: int) -> bool:
    if not path.is_file() or path.stat().st_size != size:
        return False
    checksum = 0
    with path.open("rb") as csv_file:
        for chunk in iter(lambda: csv_file.read(CHUNK_SIZE), b""):
            checksum = crc32(chunk, checksum)
    return checksum == expected_crc


def extract_csv(archive_path: Path) -> None:
    csv_path = archive_path.with_suffix("")
    with ZipFile(archive_path) as archive:
        member = archive.getinfo(csv_path.name)
        if matches_csv(csv_path, member.file_size, member.CRC):
            print(f"CSV already verified: {csv_path.name}")
            return
        with NamedTemporaryFile(dir=csv_path.parent, suffix=".part", delete=False) as temporary:
            temporary_path = Path(temporary.name)
        try:
            with archive.open(member) as source, temporary_path.open("wb") as output:
                copyfileobj(source, output, CHUNK_SIZE)
            temporary_path.replace(csv_path)
            print(f"Extracted: {csv_path.name}")
        finally:
            temporary_path.unlink(missing_ok=True)


def main() -> None:
    destination = Path(__file__).resolve().parent.parent / "data" / "raw"
    try:
        destination.mkdir(parents=True, exist_ok=True)
        for filename, checksum in ARCHIVES.items():
            archive_path = destination / filename
            download_archive(archive_path, checksum)
            extract_csv(archive_path)
    except (BadZipFile, KeyError, OSError, ValueError) as error:
        raise SystemExit(f"Dataset setup failed: {error}") from None
    print(f"Trip CSVs are available in {destination}")


if __name__ == "__main__":
    main()
