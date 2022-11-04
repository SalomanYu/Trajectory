#!/bin/bash

sudo apt install default-jdk 
sudo curl -sS -o – https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add
sudo bash -c “echo ‘deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main’ >> /etc/apt/sources.list.d/google-chrome.list”

sudo apt-get update
sudo apt-get install google-chrome-stable 

google-chrome-stable --version