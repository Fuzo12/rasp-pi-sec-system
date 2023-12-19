#Requirements:
 1. Raspberry Pi OS (Legacy) with desktop
    Release date: December 5th 2023
    System: 32-bit
    Kernel version: 6.1
    Debian version: 11 (bullseye)
    Size: 894MB

 2. Enable the I2C feature using:
    >> raspi-config
    >> Interface Options -> Legacy Camera
    >> Interface Options -> I2C

 4. Command line installments:
     >> sudo apt-get install libi2c-dev
     >> sudo pip3 install smbus2
     >> sudo reboot
     >> sudo raspi-config
     >> #check if is detected
     >> i2cdetect -y 1 
