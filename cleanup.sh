#!/usr/bin/env bash
# Cleanup script: removes Ollama installation + Vulkan/Intel GPU compute setup
# Run with: sudo bash cleanup_ollama_vulkan.sh

set -e

echo "=== Step 1: Stopping and removing Ollama service ==="
sudo systemctl stop ollama 2>/dev/null || echo "  (ollama service not running or not found)"
sudo systemctl disable ollama 2>/dev/null || echo "  (ollama service not enabled)"
sudo rm -f /etc/systemd/system/ollama.service
sudo systemctl daemon-reload

echo "=== Step 2: Removing Ollama binary ==="
sudo rm -f /usr/local/bin/ollama

echo "=== Step 3: Removing Ollama models and data (this frees the most disk space) ==="
sudo rm -rf /usr/share/ollama
rm -rf ~/.ollama

echo "=== Step 4: Removing ollama system user/group (if present) ==="
if id "ollama" &>/dev/null; then
    sudo userdel ollama
    sudo groupdel ollama 2>/dev/null || true
else
    echo "  (no ollama user found)"
fi

echo "=== Step 5: Removing Vulkan / Intel GPU compute packages ==="
sudo apt-get remove -y --purge \
    vulkan-tools \
    mesa-vulkan-drivers \
    intel-opencl-icd \
    libvulkan1 \
    clinfo \
    intel-level-zero-gpu \
    level-zero 2>/dev/null || echo "  (some packages were already absent)"

echo "=== Step 6: Removing kisak-mesa PPA (if added) ==="
if grep -q "kisak/kisak-mesa" /etc/apt/sources.list.d/*.list 2>/dev/null; then
    sudo add-apt-repository --remove ppa:kisak/kisak-mesa -y
else
    echo "  (kisak-mesa PPA not found, skipping)"
fi

echo "=== Step 7: Cleaning up unused dependencies and apt cache ==="
sudo apt-get autoremove -y
sudo apt-get autoclean -y

echo "=== Step 8: Verifying removal ==="
hash -r
echo "ollama binary check:"
which ollama 2>/dev/null && echo "  WARNING: ollama still found in PATH" || echo "  OK: ollama removed"
echo "vulkaninfo check:"
which vulkaninfo 2>/dev/null && echo "  WARNING: vulkaninfo still found" || echo "  OK: vulkan-tools removed"

echo ""
echo "=== Cleanup complete ==="
