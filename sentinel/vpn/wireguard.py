# coding=utf-8
import subprocess
import time
from thread import start_new_thread

from configparser import ConfigParser
from ..config import WIREGUARD_DIR
from ..node import node
from .utils import convert_bandwidth, convert_to_seconds


import logging

class Wireguard(object):
    def __init__(self, show_output=True):

        self.init_cmd = 'sh /root/sentinel/shell_scripts/init.sh'
        self.start_cmd = 'wg-quick up wg0'
        self.stop_cmd = 'wg-quick down wg0'
        self.add_peer_cmd = 'wg addconf wg0 {}'
        self.getsession_cmd = 'wg show wg0'
        self.allocated_ips = {}
        self.logger = logging.getLogger(__name__)

        if show_output is False:
            self.init_cmd += ' >> /dev/null 2>&1'
            self.start_cmd += ' >> /dev/null 2>&1'
        check_wg_proc = subprocess.Popen(
            self.getsession_cmd, shell=True, stdout=subprocess.PIPE)
        check_wg_proc.wait()
        if check_wg_proc.stdout.read():
            remove_old_wg_proc = subprocess.Popen(
                self.stop_cmd, shell=True, stderr=subprocess.PIPE)
            remove_old_wg_proc.wait()
            if not 'ip link delete dev wg0' in remove_old_wg_proc.stderr.read():
                logger.error("Interface can't be disconnected")
                exit()
        init_proc = subprocess.Popen(self.init_cmd, shell=True)
        init_proc.wait()
        time.sleep(2)
        with open("{}publickey".format(WIREGUARD_DIR), 'r') as f:
            node.config['wireguard']['pub_key'] = f.readline().strip()

    def start(self):
        self.vpn_proc = subprocess.Popen(
            self.start_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.vpn_proc.wait()

    def stop(self):
        kill_proc = subprocess.Popen(self.stop_cmd, shell=True)
        kill_proc.wait()

    def check_connection(self, pub_key):

        time.sleep(150)
        from ..helpers import end_session as session_end
        proc = subprocess.Popen(
            'wg show wg0 latest-handshakes', shell=True, stdout=subprocess.PIPE)
        proc.wait()
        for i in proc.stdout.read().splitlines():
            a = i.split('\t')
            if pub_key in a and int(a[-1]) == 0:
                self.logger.info('client recivied credantials but not connected')
                session_end(pub_key, 'NOT_CONNECTED')
                break

    def add_peer(self, pub_key):
        random_ip = ''
        file_path = WIREGUARD_DIR + 'client-{}'.format(pub_key[:4])
        i = 2

        while i < 255:
            if '10.0.0.{}'.format(str(i)) not in self.allocated_ips.values():
                random_ip = '10.0.0.{}'.format(str(i))
                self.allocated_ips[pub_key] = random_ip
                break
            i += 1
        config = ConfigParser()
        config['Peer'] = {
            'PublicKey': pub_key,
            'AllowedIPs': random_ip
        }
        try:
            with open(file_path, 'w+') as f:
                config.write(f)
        except Exception as err:
            return None, None, err
        
        wg_addconf_proc = subprocess.Popen(self.add_peer_cmd.format(
            file_path), shell=True, stderr=subprocess.PIPE)
        wg_addconf_proc.wait()
        error = wg_addconf_proc.stderr.read()
        if error:
            return None, None, error
        
        start_new_thread(self.check_connection, (pub_key,))

        peer_proc = subprocess.Popen(
            'wg show wg0 peers', shell=True, stdout=subprocess.PIPE)
        peer_proc.wait()
        public_keys = peer_proc.stdout.read().splitlines()
        if pub_key in public_keys:
            return {
                "Publickey": node.config['wireguard']['pub_key'],
                "EndPoint": node.ip + ":" + str(node.config['wireguard']['port']),
                "AllowedIPs": '0.0.0.0/0',
                "PersistentKeepAlive": 21,
                "ip": random_ip
            }, pub_key, None
        else:
            return None, None, "public key not added to the wireguard interface"

       

    def parse_wg_data(self):
        session_proc = subprocess.Popen(
            self.getsession_cmd, shell=True, stdout=subprocess.PIPE)
        session_proc.wait()
        lines_list = session_proc.stdout.read().splitlines()
        parsed_config = []
        pub_key, time_secs, usage = None, None, None
        for line in lines_list:
            if 'peer' in line:
                pub_key = line.split(':')[-1].strip()
            if 'latest handshake' in line:
                line = line.split(':')
                time_secs = int(convert_to_seconds(line[-1].strip()))
            if 'transfer' in line:
                line = line.split(':')
                usage = convert_bandwidth(line[-1].strip())
            if pub_key and time_secs and usage:
                parsed_config.append({
                    'pub_key': pub_key,
                    'latest_handshake': time_secs,
                    'usage': usage
                })
                pub_key, usage, time_secs = None, None, None
        return parsed_config

    def disconnect_client(self, pub_key):
        cmd = 'wg set wg0 peer {} remove'.format(pub_key)
        disconnect_proc = subprocess.Popen(
            cmd, shell=True, stderr=subprocess.PIPE)
        disconnect_proc.wait()
        error = disconnect_proc.stderr.read()
        if error:
            
            return False, error
        if pub_key in self.allocated_ips:
            self.allocated_ips.pop(pub_key)
        return True, None


wireguard = Wireguard()
