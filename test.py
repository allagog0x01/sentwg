import unittest
import requests
import json
import time
import subprocess

class API_Testing(unittest.TestCase):
    account_addr = 'cosmosaccaddr1dfjwc86e2lta7ekn4utsmxzgnhxx9mf6ytc8xy'
    session_id = '2wst8he87qklt5lhtas'
    token = '2wst834567qwerty01'
    pub_key = 'Qp3K6i+Lseq913+JFmlCk0H2BqNsdazChPXieF8mMVI='
    outputs = []

    def test_1_add_session_details(self):
        url = 'http://35.200.183.162:3000/clients/{0}/sessions/{1}'.format(self.account_addr,self.session_id)
        res = requests.post(url, data=json.dumps({'token': self.token}))
        self.assertTrue(res.json()['success'])
        self.outputs.append(res.json())
        #time.sleep(10)

    def test_2_get_vpn_credentials(self):

        url = 'http://35.200.183.162:3000/clients/{0}/sessions/{1}/credentials'.format(self.account_addr,self.session_id)
        res = requests.post(url, data=json.dumps({'token': self.token, 'pub_key': self.pub_key}))
       	proc = subprocess.Popen('wg-quick up wg0',shell = True)
       	proc.wait()
        self.assertTrue(res.json()['success'])
        self.outputs.append(res.json())
        time.sleep(5)

    def test_3_get_usage(self):
        url = 'http://35.200.183.162:3000/clients/{0}/sessions/{1}/usage'.format(self.account_addr, self.session_id)
        res = requests.post(url, data=json.dumps({'token': self.token}))
        self.assertTrue(res.json()['success'])
        self.outputs.append(res.json())
        time.sleep(5)
    
    def test_4_disconnect_client(self):
    	proc2 = subprocess.Popen('wg-quick down wg0', shell = True)
    	proc2.wait()
    	time.sleep(5)
    	url = 'http://35.200.183.162:3000/clients/{0}/sessions/{1}/disconnect'.format(self.account_addr, self.session_id)
    	res = requests.post(url, data=json.dumps({'token': self.token}))
    	self.assertTrue(res.json()['success'])
    	self.outputs.append(res.json())
    
    def test_5_out(self):
        print(self.outputs)    	  	
	

if __name__ == '__main__':
    unittest.main()
    
    
