#!/bin/bash
# deploy-solaripple.sh
# 同步本地 solaripple-web 到服务器，并备份到 GitHub

set -e

SRC=~/solaripple-web
DEST=root@47.100.20.52:/usr/share/nginx/html
KEY=~/clawd/rippleware/keys/solaripple.pem

echo "=== 1. 同步到 GitHub ==="
cd $SRC
git add -A
read -p "Commit message: " msg
git commit -m "$msg"
git push origin main

echo "=== 2. 同步到服务器 ==="
rsync -e "ssh -i $KEY -o StrictHostKeyChecking=no" -av --exclude='.bak' --exclude='.git' $SRC/ $DEST/

echo "=== 3. 验证 ==="
curl -s -o /dev/null -w "solaripple.com: %{http_code}\n" https://solaripple.com
curl -s -o /dev/null -w "www.solaripple.com: %{http_code}\n" https://www.solaripple.com

echo "=== 完成 ==="
