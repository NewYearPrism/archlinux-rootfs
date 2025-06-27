Arch has its official project for WSL, see [the Wiki](https://wiki.archlinux.org/title/Install_Arch_Linux_on_WSL)

# Arch Linux Rootfs
Rootfs tarball of [Arch Linux](https://archlinux.org), converted from the [bootstrap tarballs](https://geo.mirror.pkgbuild.com/iso/latest/) by unwraping `root.x86_64/`.

## Use in [WSL2](https://learn.microsoft.com/windows/wsl/about)
WSL2 allows you to [create a VM simply with a rootfs archive](https://learn.microsoft.com/windows/wsl/basic-commands#import-a-distribution). For example,
```Powershell
wsl.exe --import arch . .\archlinux-rootfs-2025.02.01-x86_64.tar.zst
```

## Use in LXC
Should be OK. Have not tested yet.

## Build

### Requirements
The build script needs Internet connection to check latest version of Arch Linux ISO and download file. To completely avoid network access, place the bootstrap .tar.zst file with yyyy.MM.dd formatted date in filename in ```outputs/``` (in current working directory) and set environment variable ```ARCHLINUX_ISO_VERSION``` to the corresponding date.

```Powershell
> ls .\outputs\

    Directory: D:\dev\archlinux-rootfs\outputs

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---            2025/2/4     1:47      139138439 archlinux-bootstrap-2025.02.01-x86_64.tar.zst
> $env:ARCHLINUX_ISO_VERSION="2025.02.01"

```

The script does not extract any file in tarball to file system, so it works fine on Windows. Other OS should have no problem.

> *I've tried extract Arch Linux bootstrap archive on Windows using 7zip and GNU tar in MSYS2, only to get tons of error messages saying that they could not handle the hard links and symbolic links.*

### Run the Script

Recommended way: [Install uv](https://docs.astral.sh/uv/getting-started/installation/), clone this repo, ```cd``` into it and run:
```Powershell
uv.exe run run.py
# That's it. Then uv will automatically download all the stuff it needs and run the script.
```

Or you could use any Python environment you like :)

If no error occurs, we will have 2 files under ```outputs/``` (in current working directory):

- Original bootstrap archive: 
  - archlinux-bootstrap-[DATE]-x86_64.tar.zst
- Generated rootfs archive:
  - archlinux-rootfs-[DATE]-x86_64.tar.zst
  
### Parameters

#### Environment Variables

1. ```ARCHLINUX_MIRROR``` 
    
    Replace default download site ```https://geo.mirror.pkgbuild.com/```, MUST have subdirectory ```iso/```.
    ```Powershell
    $env:ARCHLINUX_MIRROR="https://mirrors.aliyun.com/archlinux/"
    ```

1. ```ZSTD_CLEVEL```
    
    [Zstandard compression level](https://github.com/facebook/zstd/blob/dev/programs/README.md#passing-parameters-through-environment-variables). Default is 3. Bigger leads to better compression ratio but takes longer.
    ```Powershell
    $env:ZSTD_CLEVEL=9
    ```

1. ```ARCHLINUX_ISO_VERSION```
   
   Force the version. Can be use to prevent network connection.
   ```Powershell
   $env:ARCHLINUX_ISO_VERSION="2025.02.01"
   ```

Others inherited from dependencies probably work (e.g. ```HTTPS_PROXY```).

## Acknowledgement
Special thanks
- https://github.com/harenayo/archlinux-rootfs
- https://github.com/yuk7/ArchWSL
