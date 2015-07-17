#!/bin/bash

# to start
# ssh userrrrrrrrrr@hostttttttttttttt "sudo -i; wget http://ptraffer.ru/3proxy.sh && chmod +x 3proxy.sh && ./3proxy.sh"

if (( $EUID != 0 )); then
	echo "Run this script only from root! Continue?";
	read
fi

apt-get update
apt-get install nano wget make gcc mc -y

rm -f 3proxy-0.6.1.tgz
rm -rf ./3proxy-0.6.1

wget http://3proxy.ru/0.6.1/3proxy-0.6.1.tgz
tar -xvzf 3proxy-0.6.1.tgz
cd 3proxy-0.6.1

make -f Makefile.Linux

mkdir /usr/local
mkdir /usr/local/etc
mkdir /usr/local/etc/3proxy
mkdir /usr/local/etc/3proxy/bin
mkdir /usr/local/etc/3proxy/logs
mkdir /usr/local/etc/3proxy/stat

rm -f /usr/local/etc/3proxy/3proxy.cfg

cp src/3proxy /usr/local/etc/3proxy/bin

echo "daemon" >> /usr/local/etc/3proxy/3proxy.cfg
echo "auth strong" >> /usr/local/etc/3proxy/3proxy.cfg

echo "users goemailgo:CL:qifj2lI" >> /usr/local/etc/3proxy/3proxy.cfg

echo "socks -n -a -p3128" >> /usr/local/etc/3proxy/3proxy.cfg
echo "flush" >> /usr/local/etc/3proxy/3proxy.cfg
echo "allow *" >> /usr/local/etc/3proxy/3proxy.cfg

line="* * * * * pgrep 3proxy || /usr/local/etc/3proxy/bin/3proxy /usr/local/etc/3proxy/3proxy.cfg"
(crontab -l | grep -v 3proxy; echo "$line" ) | crontab -

line="@reboot pgrep 3proxy || /usr/local/etc/3proxy/bin/3proxy /usr/local/etc/3proxy/3proxy.cfg"
(crontab -l; echo "$line" ) | crontab -

echo "All ok!"
