#!/bin/bash
# install.sh — نصب سریع رخش در ترموکس و لینوکس

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[رخش] نصب در حال انجام..."

# ایجاد دایرکتوری کانفیگ
mkdir -p "$HOME/.config/rakhsh"

# کپی باینری (در صورت نیاز)
if [ -f "$SCRIPT_DIR/rakhsh" ]; then
    chmod +x "$SCRIPT_DIR/rakhsh"
    echo "[✓] اسکریپت اصلی آماده است: $SCRIPT_DIR/rakhsh"
fi

# بررسی Python
if command -v python3 >/dev/null 2>&1; then
    echo "[✓] Python3 موجود است."
else
    echo "[!] لطفاً Python3 را نصب کنید (Termux: pkg install python)"
fi

# راهنمای نصب باینری‌ها
cat << 'BANNER'

╔════════════════════════════════════════════════╗
║  رخش نصب شد!                                    ║
║                                                 ║
║  برای استفاده:                                  ║
║    ./rakhsh                                      ║
║                                                 ║
║  مطمئن شوید باینری‌های هسته در PATH هستند:      ║
║    - aether                                      ║
║    - sing-box                                    ║
║    - xray                                        ║
╚════════════════════════════════════════════════╝
BANNER
