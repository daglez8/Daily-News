#!/bin/bash
# One-time: securely save your GitHub token to the macOS keychain so pushes work.
# Your token is NOT shown on screen and is NOT stored in any file.
echo "Paste your GitHub token, then press Enter."
echo "(It stays hidden — you will NOT see anything as you paste. That's normal.)"
echo
read -rs TOKEN
echo
LEN=${#TOKEN}
echo "Captured a token of length: $LEN characters"
if [ "$LEN" -lt 20 ]; then
  echo "❌ Too short / empty — the paste didn't register."
  echo "   Tip: click inside this window first, then press Cmd+V, then Enter. Run the file again."
  exit 1
fi
case "$TOKEN" in
  github_pat_*|ghp_*) echo "✅ Format looks correct." ;;
  *) echo "⚠️  Doesn't start with github_pat_ or ghp_ — make sure you copied the whole token." ;;
esac
# Clear any old/bad entry, then store the new one
printf "protocol=https\nhost=github.com\n\n" | git credential-osxkeychain erase
printf "protocol=https\nhost=github.com\nusername=daglez8\npassword=%s\n\n" "$TOKEN" | git credential-osxkeychain store
echo "✅ Saved to keychain. Tell Claude 'done' and it will push."
