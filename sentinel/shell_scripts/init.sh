#!/bin/sh

SYSCTL=/etc/sysctl.conf
VPNCONFIG=/etc/wireguard/wg0.conf
VPNDIR=/etc/wireguard

echo 'net.ipv4.ip_forward = 1' > ${SYSCTL} && sysctl -p ${SYSCTL} && \

umask 077
wg genkey > ${VPNDIR}/private
wg pubkey < ${VPNDIR}/private > ${VPNDIR}/publickey
echo '[Interface]' > ${VPNCONFIG} && \
echo 'Address = 10.0.0.1/24' >> ${VPNCONFIG} && \
echo 'DNS = 208.67.222.222,208.67.220.220' >> ${VPNCONFIG} && \
echo 'ListenPort = 5253' >> ${VPNCONFIG} && \
echo 'PrivateKey = '$(cat $VPNDIR/private) >> ${VPNCONFIG}

iptables -t nat -A POSTROUTING -o eth0  -j MASQUERADE
iptables-save
# Firewall


