# Rakhsh — Interactive CLI for Network Core Management

Version: 1.0.0 | Platforms: Linux, Termux
Cores (Bundled): Aether (MASQUE) | Sing-Box | XRay
Port: 1819

## Quick Start

```bash
unzip rakhsh.zip
cd rakhsh
chmod +x rakhsh
python3 rakhsh --version
```

## Usage

Interactive mode (default):
```bash
python3 rakhsh
```

Quick CLI:
```bash
python3 rakhsh --start --core aether --protocol masque --port 1819
python3 rakhsh --stop
python3 rakhsh --status
```

## Features
- Fully English interface
- Bundled binaries: Aether, Sing-Box, XRay (no extra downloads needed)
- Interactive color menu
- Protocol switching (MASQUE, WireGuard, VLESS, Reality, etc.)
- Process management with PID tracking
- Config auto-generation
- Termux compatible
