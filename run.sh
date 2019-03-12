#!/bin/sh

cd /root;
nohup mongod >> /dev/null & sleep 1;
gaiacli advanced rest-server --chain-id Sentinel-dev-testnet --node http://209.182.217.171:26657 --home /root/.sentinel & sleep 1;
cp config /root/.sentinel/
python app.py
