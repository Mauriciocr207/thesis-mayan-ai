#!/bin/bash
set -e

# System dependencies
sudo apt update
sudo apt install -y python3-tk portaudio19-dev

# Install nvm (only if missing)
export NVM_DIR="$HOME/.nvm"

if [ ! -s "$NVM_DIR/nvm.sh" ]; then
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash
fi

# Load nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Install Node LTS (NO 24 en scripts)
nvm install --lts
nvm use --lts

# Verify
echo "================================="
echo "Setup completo"
echo "================================="
echo ""
echo "Recarga tu terminal con:"
echo "  source ~/.bashrc  (o ~/.zshrc)"
echo ""
echo "Luego verifica con:"
echo "  node -v"
echo "  npm -v"
echo "================================="