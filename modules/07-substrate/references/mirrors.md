# Alibaba artifactory reference (live-verified)

Two hosts, same content: `http://mirrors.cloud.aliyuncs.com` (VPC-internal, HTTP — pass `--trusted-host mirrors.cloud.aliyuncs.com`; HTTPS on this host is dead) and `https://mirrors.aliyun.com` (public). cloud host redirects some paths to aliyun http — add both trusted-hosts when using HTTP indexes.

Live repos (38, probed in parallel): alinux, alpine, anaconda, apt, archlinux, bioconductor, blender, centos, centos-vault, composer, cygwin, debian, debian-security, docker-ce, elasticstack, epel, fedora, gimp, gitlab-ce, gnu, golang, gradle, grafana, homebrew, homebrew-bottles, jenkins, kali, kubernetes, libreoffice, maven, mongodb, mysql, nodejs-release, postgresql, puppet, pypi, pytorch-wheels, rustup, saltstack, termux, ubuntu, ubuntu-ports, videolan, zabbix. Full map with preferred host: `/mnt/agents/output/av/repos.json` (regenerate: `search.py repos`).

Notes:
- pypi: `<host>/pypi/simple/` — PEP 503, pip-ready.
- pytorch-wheels: HTML portal, NOT a pip simple index — pip cannot consume it. For CPU-only torch use `https://download.pytorch.org/whl/cpu` (raced automatically by loader.py); aliyun pypi fallback ships the large CUDA-bundled wheel — install with `--no-deps` plus pure-python deps (filelock, typing-extensions, sympy, networkx, jinja2, fsspec, mpmath) to stay CPU-only.
- apt/ubuntu/debian repos work as standard deb sources; anaconda/miniconda installers under `/anaconda/`.
- Other fallbacks in chain: tuna (`https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple/`), ustc (`https://mirrors.ustc.edu.cn/pypi/web/simple/`), pypi.org.
