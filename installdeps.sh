#!/bin/bash

echo "Updating package lists..."
sudo apt update
echo "Installing python3-apt..."
sudo apt install -y python3-apt
echo "Installing python3.12-distutils..."
sudo apt install -y python3.12-distutils
echo "Reinstalling python3-apt (optional)..."
sudo apt remove --purge -y python3-apt
sudo apt install -y python3-apt
echo "Dependencies installed successfully!"
