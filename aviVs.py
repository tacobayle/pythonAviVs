from avi.sdk.avi_api import ApiSession
import sys, json
#
# Variables
#
fileCredential = sys.argv[1]
tenant = "admin"
objectPrefix = 'python-'
#
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
#
# Avi class
#
class aviSession:
  def __init__(self, fqdn, username, password, tenant):
    self.fqdn = fqdn
    self.username = username
    self.password = password
    self.tenant = tenant

  def debug(self):
    print("controller is {0}, username is {1}, password is {2}, tenant is {3}".format(self.fqdn, self.username, self.password, self.tenant))

  def retrieveDomainName(self):
    api = ApiSession.get_session(self.fqdn, self.username, self.password, self.tenant)
    ipamdnsproviderprofile = api.get('ipamdnsproviderprofile')
    for item in ipamdnsproviderprofile.json()['results']:
        if item['type'] == 'IPAMDNS_TYPE_INTERNAL_DNS':
            domainName = item['internal_profile']['dns_service_domain'][0]['domain_name']
            break
    return domainName

  def retrieveNetwork(self):
    api = ApiSession.get_session(self.fqdn, self.username, self.password, self.tenant)
    ipamdnsproviderprofile = api.get('ipamdnsproviderprofile')
    for item in ipamdnsproviderprofile.json()['results']:
        if item['type'] == 'IPAMDNS_TYPE_INTERNAL':
            networkUuid = item['internal_profile']['usable_network_refs'][0].split('/network/')[1]
            break
    return networkUuid

  def retrieveNetworkNameMaskType(self, networkUuid):
    api = ApiSession.get_session(self.fqdn, self.username, self.password, self.tenant)
    network = api.get('network?page_size=-1')
    for item in network.json()['results']:
        if item['uuid'] == networkUuid:
            name = item['name']
            mask = item['configured_subnets'][0]['prefix']['mask']
            network = item['configured_subnets'][0]['prefix']['ip_addr']['addr']
            type = item['configured_subnets'][0]['prefix']['ip_addr']['type']
            break
    return name, network, mask, type

  def getObjByName(self, object, objectName):
    api = ApiSession.get_session(self.fqdn, self.username, self.password, self.tenant)
    return api.get_object_by_name(object, objectName)

  def configureMyObjectMyData(self, myObject, myData):
    api = ApiSession.get_session(self.fqdn, self.username, self.password, self.tenant)
    myResult = api.post(myObject, data=myData)
    return myResult
#
# Main Pyhton script
#
if __name__ == '__main__':
    with open(fileCredential, 'r') as stream:
        credential = json.load(stream)
    stream.close
    defineClass = aviSession(credential['avi_credentials']['controller'], credential['avi_credentials']['username'], credential['avi_credentials']['password'], tenant)
    domainName = defineClass.retrieveDomainName()
    networkUuid = defineClass.retrieveNetwork()
    networkName, networkAddress, networkMask, networkType = defineClass.retrieveNetworkNameMaskType(networkUuid)
    #print('Network Name is {0}, Network Address is {1}, Network mask is {2}, Network type is {3}'.format(networkName, networkAddress, networkMask, networkType))
    #
    # Create a hmData variable to be used when creating the health monitor
    #
    hmData = {
      "receive_timeout": hmHttpRt,
      "name": objectPrefix + hmHttpName,
      "failed_checks": hmHttpFc,
      "send_interval": hmHttpSi,
      "http_monitor": {
        "http_request": hmHttpR,
        "http_response_code": hmHttpRc
      },
      "successful_checks": hmHttpSc,
      "type": hmHttpType
    }
    print(defineClass.configureMyObjectMyData('healthmonitor', hmData))
    #
    # Create a poolData variable to be used when creating the pool
    #
    servers = []
    for server in poolServerList:
        serverDict = {}
        serverDict['addr'] = server
        serverDict['type'] = 'V4'
        IpDict = {}
        IpDict['ip'] = serverDict
        servers.append(IpDict)
    poolData = {
      "name": objectPrefix + poolName,
      "lb_algorithm:": poolA,
      "health_monitor_refs": ['/api/healthmonitor?name=' + objectPrefix + hmHttpName],
      "servers": servers
    }
    print(defineClass.configureMyObjectMyData('pool', poolData))
    #
    # Create a list of services (with ssl enabled if tcp port == 443)
    #
    services = []
    for port in vsPorts:
        serviceDict = {}
        serviceDict['port'] = port
        if port != 443:
            serviceDict['enable_ssl'] = 'false'
        else:
            serviceDict['enable_ssl'] = 'true'
        services.append(serviceDict)
    #
    # Create a vsData variable to be used when creating the VS
    #
    vsData = {
      "name": objectPrefix + vsName,
      "ssl_profile_ref": "/api/sslprofile?name=" + vsSslProfile,
      "ssl_key_and_certificate_refs": "/api/sslkeyandcertificate?name=" + vsSslCertificate,
      "services" : services,
      "pool_ref": defineClass.getObjByName('pool', poolData['name'])['uuid'],
      "subnet_uuid": networkUuid,
      "auto_allocate_ip": "true",
      "dns_info": [{"fqdn": objectPrefix + vsName + '.' + domainName}]
    }
    print(defineClass.configureMyObjectMyData('virtualservice', vsData))
