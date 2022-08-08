#!/bin/bash

unzip chromedriver_linux64.zip 

sudo mv chromedriver /usr/bin/chromedriver
sudo chown root:root /usr/bin/chromedriver
sudo chmod +x /usr/bin/chromedriver 

wget https://github.com/SeleniumHQ/selenium/releases/download/selenium-4.1.0/selenium-server-4.1.2.jar
mv selenium-server-4.1.2.jar selenium-server.jar

sudo apt install xvfb
xvfb-run java -Dwebdriver.chrome.driver=/usr/bin/chromedriver -jar selenium-server.jar