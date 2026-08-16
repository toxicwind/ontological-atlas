#!/bin/bash
# auto_fix_env.sh: Run before every command to ensure environment is correct
set -e

# Git safety
git config --global --add safe.directory '*' 2>/dev/null || true
git config --global user.name "toxicwind" 2>/dev/null || true
git config --global user.email "toxicwind@users.noreply.github.com" 2>/dev/null || true

# Permissions
chmod -R 777 /mnt/agents/output/av 2>/dev/null || true
chown -R $(whoami) /mnt/agents/output/av 2>/dev/null || true
chmod -R 777 /mnt/agents/output/ontological-atlas 2>/dev/null || true

# Python path
export PYTHONUSERBASE=/home/kimi/.local
export PATH="/home/kimi/.local/bin:$PATH"

# Pip mirrors
export PIP_INDEX_URL=http://mirrors.cloud.aliyuncs.com/pypi/simple/
export PIP_TRUSTED_HOST=mirrors.cloud.aliyuncs.com

echo "ENV_FIXED"
