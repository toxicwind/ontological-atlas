# Kernel Audit — System Environment

## Kernel Identity
- Python: 3.12.12 (GCC 12.2.0)
- Executable: /usr/local/bin/python3
- Platform: linux
- PID: 341
- PPID: 61 (kernel_server.py)
- UID: 999 (kimi)
- GID: 995
- CWD: /mnt/agents

## Registered Magics

### Line Magics (101 total)
alias, alias_magic, autoawait, autocall, automagic, autosave, bookmark, cat, cd, clear, code_wrap, colors, conda, config, connect_info, cp, debug, dhist, dirs, doctest_mode, ed, edit, env, gui, hist, history, killbgscripts, ldir, less, lf, ll, load, load_ext, loadpy, logoff, logon, logstart, logstate, ls, lsmagic, lx, macro, magic, man, matplotlib, mkdir, more, mv, notebook, page, pastebin, pdef, pdoc, pfile, pinfo, pinfo2, pip, popd, pprint, prun, psearch, psource, pushd, pwd, pycat, pylab, quickref, recall, rehashx, reload_ext, rep, rerun, reset, reset_selective, rm, rmdir, run, save, sc, set_env, store, sx, system, tb, time, timeit, unalias, unload_ext, who, who_ls, whos, xdel, xmode

### Cell Magics (28 total)
!, HTML, SVG, bash, capture, code_wrap, debug, file, html, javascript, js, latex, markdown, perl, prun, pypy, python, python2, python3, ruby, script, sh, svg, sx, system, time, timeit, writefile

## The "Dash" Pattern

The `mshtools-` prefix uses a dash as namespace separator:
- `mshtools-shell` (not mshtools_shell)
- `mshtools-read_file`
- `mshtools-edit_file`

This is XML-safe naming. Dashes are valid in XML tags; underscores are also valid but the system uses dashes for visual separation between namespace and tool name.

The `!` magic is shell execution. The `%%bash` cell magic is preferred for multi-line. The `%` line magic is for single-line.

## Network Topology

| Port | Hex | Service | Process |
|------|-----|---------|---------|
| 22 (0x16) | SSH | sshd |
| 8888 (0x22B8) | Jupyter kernel API | kernel_server.py |
| 9222 (0x2406) | Chrome remote debugging | chromium |
| 9223 (0x2407) | CDP socat proxy | socat |
| 6080 (0x17C0) | KasmVNC websocket | Xvnc |
| 5901 (0x170D) | VNC RFB | Xvnc |

## CDP Browser

- Chrome 149.0.7827.196
- WebSocket: ws://127.0.0.1:9223/devtools/browser/a601b72a-d876-4a1b-a9c9-0a97bcc522f5
- Proxy: 10.86.13.73:5900
- User data: /app/data/chrome_data
- Flags: --no-sandbox, --single-process, --disable-gpu, --remote-debugging-port=9222

## S6 Init System

Services under /run/service:
- kasmvnc
- sshd
- kernel-server
- s6rc-oneshot-runner
- browser-guard
- socat

## Key Processes

| PID | User | Command |
|-----|------|---------|
| 1 | root | s6-svscan |
| 50 | kimi | browser_guard.py |
| 61 | kimi | kernel_server.py (port 8888) |
| 116 | root | Xvnc (VNC + websocket) |
| 139 | kimi | ipykernel_launcher |
| 148 | kimi | playwright driver |
| 265 | kimi | chromium (Chrome 149) |
| 281-284 | kimi | chrome_crashpad_handler |

## Environment Variables

- HOME: /home/kimi
- PYTHONUNBUFFERED: 1
- PYTHONUSERBASE: /home/kimi/.local
- SSH_PASSWORD: [redacted]
- VNC_PASSWORD: [redacted]
- PATH: includes /home/kimi/.local/bin

## The Tool Invocation Mechanism

Tools are invoked via XML tags in the assistant's output:
```xml
<mshtools-shell>
{"command": "ls", "description": "List files"}
</mshtools-shell>
```

The system parses these tags, executes the tool, and returns results. The 25-step limit per turn controls how many tool calls can be made before the assistant must provide a final response.

## Proxy Configuration

Chromium runs with `--proxy-server=10.86.13.73:5900`. This is the egress proxy for web access. Direct connections to github.com:443 are blocked (TLS-flaky), but api.github.com works.
