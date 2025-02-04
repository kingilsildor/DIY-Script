#! /bin/bash
# Works on Ubuntu/Debian systems 

## Get the newest version of Obsidian .deb file
deb_link=$(curl -s https://obsidian.md/download |\
  grep -o "https://github[^0-9]*/v[0-9]\.[0-9]\.[0-9]/obsidian_[0-9]\.[0-9]\.[0-9]_amd64.deb")

wget $deb_link

## Get filename
deb_filename=$(ls | grep obsidian_[0-9]\.[0-9]\.[0-9]_amd64.deb)

## Install obsidian inside Ubuntu
sudo apt-get install -y ./$deb_filename
