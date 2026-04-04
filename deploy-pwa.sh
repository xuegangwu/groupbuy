#!/bin/bash
# Deploy PWA to Solaripple + EnOS servers
# Run after SSH is restored

set -e
SERVER="root@47.100.20.52"
KEY="~/.ssh/solaripple.pem"
DEST_SOLAR="/usr/share/nginx/html/"
DEST_ENOS="/var/www/enos/"

echo "=== Deploying Solaripple PWA ==="
# Deploy solaripple PWA files
scp -i $KEY $SERVER:$DEST_SOLAR/index.html /tmp/index_backup.html 2>/dev/null || true

# Add PWA meta tags to index.html head (sed injection)
# 1. Add manifest link
ssh -i $KEY $SERVER "grep -q 'manifest.json' $DEST_SOLAR/index.html || sed -i 's|</title>|</title><link rel=\"manifest\" href=\"/manifest.json\">|' $DEST_SOLAR/index.html"

# 2. Add theme-color meta
ssh -i $KEY $SERVER "grep -q 'theme-color' $DEST_SOLAR/index.html || sed -i 's|<meta name=\"viewport\"|<meta name=\"theme-color\" content=\"#00D4AA\">\\n  <meta name=\"viewport\"|' $DEST_SOLAR/index.html"

# 3. Add apple-touch-icon
ssh -i $KEY $SERVER "grep -q 'apple-touch-icon' $DEST_SOLAR/index.html || sed -i 's|</head>|<link rel=\"apple-touch-icon\" href=\"/icons/icon-192.png\">\\n</head>|' $DEST_SOLAR/index.html"

# 4. Link mobile CSS before </head>
ssh -i $KEY $SERVER "grep -q 'mobile.css' $DEST_SOLAR/index.html || sed -i 's|</head>|<link rel=\"stylesheet\" href=\"/mobile.css\">\\n</head>|' $DEST_SOLAR/index.html"

# 5. Link mobile.js before </body>
ssh -i $KEY $SERVER "grep -q 'mobile.js' $DEST_SOLAR/index.html || sed -i 's|</body>|<script src=\"/mobile.js\"><\\/script>\\n</body>|' $DEST_SOLAR/index.html"

# Upload PWA files
echo "Uploading manifest.json, sw.js, mobile.css, mobile.js..."
ssh -i $KEY $SERVER "mkdir -p $DEST_SOLAR/icons"
rsync -avz -e \"ssh -i $KEY\" manifest.json sw.js mobile.css mobile.js $SERVER:$DEST_SOLAR/
rsync -avz -e \"ssh -i $KEY\" icons/ $SERVER:$DEST_SOLAR/icons/

echo ""
echo "=== Deploying EnOS PWA ==="

# Add PWA meta tags to enos index.html
ssh -i $KEY $SERVER "grep -q 'manifest.json' $DEST_ENOS/index.html || sed -i 's|</title>|</title><link rel=\"manifest\" href=\"/manifest.json\">|' $DEST_ENOS/index.html"
ssh -i $KEY $SERVER "grep -q 'theme-color' $DEST_ENOS/index.html || sed -i 's|<meta name=\"viewport\"|<meta name=\"theme-color\" content=\"#00D4AA\">\\n  <meta name=\"viewport\"|' $DEST_ENOS/index.html"
ssh -i $KEY $SERVER "grep -q 'mobile.css' $DEST_ENOS/index.html || sed -i 's|</head>|<link rel=\"stylesheet\" href=\"/mobile.css\">\\n</head>|' $DEST_ENOS/index.html"
ssh -i $KEY $SERVER "grep -q 'mobile.js' $DEST_ENOS/index.html || sed -i 's|</body>|<script src=\"/mobile.js\"><\\/script>\\n</body>|' $DEST_ENOS/index.html"

# Upload EnOS PWA files
echo "Uploading EnOS manifest.json, sw.js, mobile.css, mobile.js..."
ssh -i $KEY $SERVER "mkdir -p $DEST_ENOS/icons"
rsync -avz -e \"ssh -i $KEY\" $DEST_ENOS/ manifest.json sw.js mobile.css mobile.js $SERVER:$DEST_ENOS/
rsync -avz -e \"ssh -i $KEY\" icons/ $SERVER:$DEST_ENOS/icons/

echo ""
echo "=== Fixing permissions ==="
ssh -i $KEY $SERVER "chmod -R 755 $DEST_SOLAR $DEST_ENOS"

echo ""
echo "=== Done! ==="
echo "Test on mobile:"
echo "  Solaripple: https://solaripple.com/"
echo "  EnOS:        https://enos.solaripple.com/"
echo ""
echo "To install as PWA on mobile:"
echo "  Android Chrome: menu -> Install app / 添加到主屏幕"
echo "  iOS Safari: share -> Add to Home Screen"
