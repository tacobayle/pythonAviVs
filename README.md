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
- VMware V-center


## Input/Parameters:

1. Make sure you have a json file with the Avi credentials like the following:

```
avi@ansible:~/python/aviVs$ more creds.json
{"avi_credentials": {"username": "admin", "controller": "192.168.142.135", "password": "*****", "api_version": "18.2.9"}}

```

2. All the other paramaters/variables are stored in the python script aviVs.py.
The below variable(s) called need(s) to be adjusted:
- poolServerList
The other varaiables don't need to be adjusted.

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
poolServerList = ['172.16.3.252', '172.16.3.253']
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
2. Create a Pool (based on the Health Monitor previously created)
3. Create a VS based on Avi IPAM and DNS and based on the pool previously created

## Run the terraform:
- deploy:
```
python3 aviVs.py creds.json
```

## Improvment:
- add SE service group
- add log and analytics capabilities
```
resource "avi_virtualservice" "https_vs" {
  name                          = var.vs_name
  pool_group_ref                = avi_poolgroup.poolgroup1.id
  tenant_ref                    = data.avi_tenant.default_tenant.id
  vsvip_ref                     = avi_vsvip.test_vsvip.id
  cloud_ref                     = data.avi_cloud.default_cloud.id
  ssl_key_and_certificate_refs  = [data.avi_sslkeyandcertificate.ssl_cert1.id]
  ssl_profile_ref               = data.avi_sslprofile.ssl_profile1.id
  application_profile_ref       = data.avi_applicationprofile.application_profile1.id
  network_profile_ref           = data.avi_networkprofile.network_profile1.id
  services {
    port           = var.vs_port
    enable_ssl     = true
  }
  analytics_policy {
    client_insights = "NO_INSIGHTS"
    all_headers = "false"
    udf_log_throttle = "10"
    significant_log_throttle = "0"
    metrics_realtime_update {
      enabled  = "true"
      duration = "0"
    }
    full_client_logs {
        enabled = "true"
        throttle = "10"
        duration = "30"
    }
  }
}
```
