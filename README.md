# python Avi VS

## Goals
Configure a Health Monitor, Pool and VS through Python (Python SDK)

## Prerequisites:
1. Make sure python3 is installed
2. Make sure pip install avisdk is installed:
```
pip install avisdk
```
3. Make sure your Avi Controller is reachable from your host
4. Make sure you have an IPAM/DNS profile is configured

## Environment:

### Avi version

```
Avi 18.2.9
```

### Avi Environment

- LSC Cloud


## Input/Parameters:

1. Make sure you have a json file with the Avi credentials like the following:

```
avi@ansible:~/python/aviVs$ more creds.json
{"avi_credentials": {"username": "admin", "controller": "192.168.142.135", "password": "*****", "api_version": "18.2.9"}}

```

2. All the other paramaters/variables are stored in the python script aviVs.py. The following parameters need to be changed:

```
# Health Monitor
hmHttpName = 'hm1'
hmHttpType = 'HEALTH_MONITOR_HTTP'
hmHttpRt = 1
hmHttpFc = 3
hmHttpSi = 1
hmHttpR = 'HEAD / HTTP/1.0'
hmHttpRc = ["HTTP_2XX", "HTTP_3XX", "HTTP_5XX"]
hmHttpSc = 2
#
# Pool
poolName = 'pool1'
poolA = 'LB_ALGORITHM_ROUND_ROBIN'
poolHm = hmHttpName
PoolServerList = ['172.16.3.252', '172.16.3.253']
poolPort = 80
#
# Vs
vsName = 'app1'
vsPorts = [80, 443]
vsSslProfile = 'System-Standard'
vsSslCertificate = 'System-Default-Cert'
```

## Use the the python script to:
1. Create a Health Monitor
2. Create a Pool
3. Create a VS based on Avi IPAM and DNS

## Run the terraform:
- deploy:
```
python3 aviVs.py creds.json
```

## Improvment:
