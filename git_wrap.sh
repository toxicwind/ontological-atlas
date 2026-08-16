#!/bin/bash
# git_wrap.sh: Wrapper that uses --git-dir to avoid dotfile issues
REAL_GIT_DIR="/mnt/agents/output/ontological-atlas/.git"
WORK_TREE="/mnt/agents/output/ontological-atlas"
/usr/bin/git --git-dir="$REAL_GIT_DIR" --work-tree="$WORK_TREE" "$@"
