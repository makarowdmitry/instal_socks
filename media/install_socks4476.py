#! /usr/bin/env python
import os

a = os.system("""
	service iptables stop
	service iptables save
	chkconfig iptables off
	cd /usr/local/src
	yum update -y
	yum install -y mc nano gcc make wget
	wget http://3proxy.ru/0.6.1/3proxy-0.6.1.tgz
	tar -xvzf 3proxy-0.6.1.tgz
	cd 3proxy-0.6.1
	make -f Makefile.Linux
	mkdir /usr/local/etc/3proxy
	mkdir /usr/local/etc/3proxy/bin
	mkdir /usr/local/etc/3proxy/logs
	mkdir /usr/local/etc/3proxy/stat
	cp src/3proxy /usr/local/etc/3proxy/bin
	cp ./scripts/rc.d/proxy.sh /etc/init.d/3proxy
	chkconfig 3proxy on
	""")


def create_conf_proxy(ip_serv,login_proxy,pass_proxy):
	os.chdir("/usr/local/etc/3proxy")
	# os.chdir("/home/tp")
	proxy_conf = """daemon
auth strong
users """+login_proxy+":CL:"+pass_proxy+"""
socks -n -a -p3128 -i"""+ip_serv+" -e"+ip_serv+"""
flush
allow """+login_proxy+"""
	"""
	conf_proxy_create = open("3proxy.cfg","w")
	conf_proxy_create.writelines(proxy_conf)
	conf_proxy_create.close()
	return "ok"

create_conf_proxy("85.143.218.89","goemailgo","qifj2lI")

b = os.system("""
	reboot
	""")
