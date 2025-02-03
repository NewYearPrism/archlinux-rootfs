import os
import tarfile
import urllib
import urllib.parse
import io
from pathlib import Path

import zstandard
import httpx

from loguru import logger


def main():
    mirror = os.environ.get("ARCHLINUX_MIRROR") or "https://geo.mirror.pkgbuild.com"
    zstd_clevel = int(os.environ.get("ZSTD_CLEVEL") or "3")
    logger.info(f"Archlinux mirror: {mirror}")
    version = os.environ.get("ARCHLINUX_ISO_VERSION")
    if not version:
        version_url = urllib.parse.urljoin(mirror, "iso/latest/arch/version")
        r = httpx.get(version_url)
        version = r.text.strip()
    logger.info(f"Latest ArchISO(x86_64) version: {version}")
    os.makedirs("outputs", exist_ok=True)
    boot_zst_path = Path(f"outputs/archlinux-bootstrap-{version}-x86_64.tar.zst")
    bootstrap_url = urllib.parse.urljoin(mirror, f"iso/{version}/archlinux-bootstrap-{version}-x86_64.tar.zst")
    if not boot_zst_path.is_file():
        with boot_zst_path.open("wb") as zst:
            logger.info(f"Download bootstrap from {bootstrap_url}, save to {boot_zst_path}")
            boot_resp = httpx.get(bootstrap_url)
            zst.write(boot_resp.content)
    else:
        logger.info(f"{boot_zst_path} already exists, skip downloading")
    root_zst_path = Path(f"outputs/archlinux-rootfs-{version}-x86_64.tar.zst")
    if not root_zst_path.is_file():
        root_tar_buffer = io.BytesIO()
        with boot_zst_path.open("rb") as boot_zst:
            logger.info(f"Convert bootstrap into rootfs, save to {root_zst_path}")
            zdc = zstandard.ZstdDecompressor()
            boot_tar_stream = zdc.stream_reader(boot_zst)
            with tarfile.TarFile(fileobj=boot_tar_stream, mode="r", stream=True) as boot_tar, tarfile.TarFile(
                    fileobj=root_tar_buffer, mode="w", stream=True) as root_tar:
                for member in boot_tar:
                    if member.name.startswith("root.x86_64"):
                        new_name = member.name.replace("root.x86_64", ".", 1)
                        new_member = member.replace(name=new_name)
                        if member.islnk():
                            new_linkname = member.linkname.replace("root.x86_64", ".", 1)
                            new_member = new_member.replace(linkname=new_linkname)
                        data = None
                        try:
                            data = boot_tar.extractfile(member)
                        except Exception as e:
                            logger.trace(e)
                        root_tar.addfile(new_member, data)
        with root_zst_path.open("wb") as root_zst:
            root_zst.write(zstandard.compress(root_tar_buffer.getvalue(), zstd_clevel))
    else:
        logger.info(f"{root_zst_path} already exists, skip conversion")


if __name__ == "__main__":
    main()
