#!/bin/bash

#sudo apt update && sudo apt upgrade

echo Connect /tmp/forward-proxy/proxy.sock to 127.0.0.1:8118
test -e /tmp/forward-proxy/proxy.sock && sudo rm /tmp/forward-proxy/proxy.sock
socat UNIX-LISTEN:/tmp/forward-proxy/proxy.sock,reuseaddr,fork TCP:127.0.0.1:8118 &
sudo chmod 777 /tmp/forward-proxy/proxy.sock

echo Connect /tmp/proxy/bots.sock to $REMOTEEXEC_ADDR
test -e /tmp/proxy/bots.sock && sudo rm /tmp/proxy/bots.sock
socat UNIX-LISTEN:/tmp/proxy/bots.sock,reuseaddr,fork TCP4:$REMOTEEXEC_ADDR &
sudo chmod 777 /tmp/proxy/bots.sock

echo Connect /tmp/forward-proxy/ftp.sock to 127.0.0.1:1090
/usr/sbin/danted &
test -e /tmp/forward-proxy/ftp.sock && sudo rm /tmp/forward-proxy/ftp.sock
socat UNIX-LISTEN:/tmp/forward-proxy/ftp.sock,reuseaddr,fork TCP4:127.0.0.1:1080 &
sudo chmod 777 /tmp/forward-proxy/ftp.sock

squid -N
