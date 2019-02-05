# coding=utf-8
import subprocess
import time
from thread import start_new_thread

from configparser import ConfigParser
from ..config import WIREGUARD_DIR
from ..node import node
from .utils import convert_bandwidth, convert_to_seconds

# have to add wg-quick down


class Wireguard(object):
    def __init__(self, show_output=True):

        self.init_cmd = 'sh /root/sentinel/shell_scripts/init.sh'
        self.start_cmd = 'wg-quick up wg0'
        self.stop_cmd = 'wg-quick down wg0'
        self.add_peer_cmd = 'wg addconf wg0 {}'
        self.getsession_cmd = 'wg show wg0'
        self.allocated_ips = []
        if show_output is False:
            self.init_cmd += ' >> /dev/null 2>&1'
            self.start_cmd += ' >> /dev/null 2>&1'
        init_proc = subprocess.Popen(self.init_cmd, shell=True)
        init_proc.wait()
        time.sleep(2)
        with open("{}publickey".format(WIREGUARD_DIR), 'r') as f:
            node.config['wireguard']['pub_key'] = f.readline().strip()

    def start(self):
        self.vpn_proc = subprocess.Popen(
            self.start_cmd, shell=True, stdout=subprocess.PIPE)
        self.vpn_proc.wait()

    def stop(self):
        kill_proc = subprocess.Popen(self.stop_cmd, shell=True)
        kill_proc.wait()
        if kill_proc.returncode == 0:
            self.vpn_proc, self.pid = None, None
        return kill_proc.returncode

    def check_connection(self, pub_key):

        time.sleep(300)
        from ..helpers import end_session as session_end
        parsed_config_data = self.parse_wg_data('check_connection')
        for peer in parsed_config_data:
            if peer['pub_key'] == pub_key and peer['latest_handshake'] is None:
                end, err = session_end(pub_key, 'NOT_CONNECTED')

    def add_peer(self, pub_key):
        random_ip = ''
        file_path = WIREGUARD_DIR + 'client-{}'.format(pub_key[:4])
        i = 2
        # TODO ADD A ROBUST LOGIC TO ADD RANDOM IP from 10 ip range
        # TODO INCRESE AND THE NUMBER OF IP's available.
        # TODO WHAT IF RANDOM_IP IS NOT ASSIGNED.
        while i < 255:
            if '10.0.0.{}'.format(str(i)) not in self.allocated_ips:
                random_ip = '10.0.0.{}'.format(str(i))
                self.allocated_ips.append(random_ip)
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
        # TODO: CAN YOU THINK OF EXCEPTIONS
        # print (self.add_peer_cmd.format(file_path))
        wg_addconf_proc = subprocess.Popen(self.add_peer_cmd.format(
            file_path), shell=True, stderr=subprocess.PIPE)
        wg_addconf_proc.wait()
        if wg_addconf_proc.stderr.read():
            return None, None, wg_addconf_proc.stderr.read()
        # TODO WHAT IS THE SAFEST WAY TO PROCESS COMMANDS
        start_new_thread(self.check_connection, (pub_key,))
        if pub_key in self.parse_wg_data('get_connected_pub_keys'):
            return {
                "Publickey": node.config['wireguard']['pub_key'],
                "EndPoint": node.ip + ":" + str(node.config['wireguard']['port']),
                "AllowedIPs": '0.0.0.0/0',
                "PersistentKeepAlive": 21,
                "ip": random_ip
            }, pub_key, None

        # TODO RETURNING STRUCTURE

    def parse_wg_data(self, type=''):

        session_proc = subprocess.Popen(
            self.getsession_cmd, shell=True, stdout=subprocess.PIPE)
        session_proc.wait()
        lines_list = session_proc.stdout.read().splitlines()
        parsed_config = []
        pub_key, time_secs, usage = None, None, None
        if type == 'read_connection':
            for line in lines_list:
                if 'peer' in line:
                    pub_key = line.split(':')[-1].strip()
                if 'latest handshake' in line:
                    line = line.split(':')
                    time_secs = int(convert_to_seconds(line[-1].strip()))
                if 'transfer' in line:
                    line = line.split(':')
                    usage, err = convert_bandwidth(line[-1].strip())
                    if not usage:
                        return []
                if pub_key and time_secs and usage:
                    parsed_config.append({
                        'pub_key': pub_key,
                        'latest_handshake': time_secs,
                        'usage': usage
                    })
                    pub_key, usage, time_secs = None, None, None
            return parsed_config
        if type == 'check_connection':
            for line in lines_list:
                if 'peer' in line:
                    pub_key = line.split(':')[-1].strip()
                if 'latest handshake' in line:
                    line = line.split(':')
                    time_secs = int(convert_to_seconds(line[-1].strip()))
                if pub_key:
                    parsed_config.append(
                        {'pub_key': pub_key, 'latest_handshake': time_secs})
                    pub_key, time_secs = None, None

            return parsed_config
        if type == 'get_connected_pub_keys':
            for line in lines_list:
                if 'peer' in line:
                    pub_key = line.split(':')[-1].strip()
                    parsed_config.append(pub_key)
            return parsed_config


wireguard = Wireguard()
