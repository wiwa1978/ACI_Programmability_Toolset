from acitoolkit.acitoolkit import *
import yaml
from pprint import pprint

def main():
   url = "https://sandboxapicdc.cisco.com"

   user = "admin"
   pwd = "ciscopsdt"

   session = Session(url, user, pwd)
   session.login()

   # Read YAML configuration
   # The various variables contain the values as they are read from the variables file
   yml_file = open("./vars/aci_variables.yml").read()
   yml_dict = yaml.load(yml_file, yaml.SafeLoader)

   tenant_name = yml_dict['tenant']
   vrf_name = yml_dict['vrf']
   bd_name = yml_dict['bridge_domains'][0]['bd']
   bd_subnet = yml_dict['bridge_domains'][0]['gateway'] + "/" + yml_dict['bridge_domains'][0]['mask']

   ap_name = yml_dict['ap']
   epg_name = yml_dict['epgs'][0]['epg']

   # Configure ACI

   tenant = Tenant(tenant_name)        # Create tenant with variable name for Tenant
   vrf = Context(vrf_name, tenant)     # Create VRF with variable name for VRF
  
   bd = BridgeDomain(bd_name, tenant)  # Create BD with variable name for BD
   subnet = Subnet('', bd)             # Create Subnet with variable name for Subnet and assign to BD
   subnet.addr = bd_subnet             # Specify the subnet address as read from the variables file
   subnet.set_scope('public,shared')   # Set the scope of the subnet
   bd.add_context(vrf)                 # Assign the subnet to the VRF
   bd.add_subnet(subnet)               # Add the subnet to the BD
   
   ap = AppProfile(ap_name, tenant )   # Create AP with variable name for AP
   epg = EPG(epg_name, ap)             # Create EPG with variable name for EPG and assign to AP
   
   epg.attach(bd)
   # Read all the tenants on the ACI fabric. Reason is that we need to assign a number of objects from 
   # the common tenant to the tenant we are creating.
   

   for mycontract in yml_dict['contracts']:              # Read all the contracts from the variable file
      contracts_name = mycontract['contract']
      contracts_subject = mycontract['subject']
      contracts_filter = mycontract['filter']

      contract = Contract(contracts_name, tenant)        # Create Contract object on ACI
      addFilters(contract, yml_dict['filters'])          # Function loops over the filters in the variable file and will assign them to the contract
      epg.consume(contract)                              # Attach these contracts to the EPG

   response = session.push_to_apic(tenant.get_url(), data=tenant.get_json()) #Send all the gathered information to APIC

   if not response.status_code == 200:
      print(f"Tenant {tenant} was not created successfully")
   else:
      print(f"Tenant {tenant} was created successfully")

def get_contract(session, tenant, contract_name):
    contracts = Contract.get(session, tenant)
    for contract in contracts:
      if (contract.name == contract_name):
         return contract

def addFilters(contract, filters):
   for myfilter in filters:
      filter_name = myfilter['filter']
      filter_entry = myfilter['entry']
      filter_protocol = myfilter['protocol']
      filter_port = myfilter['port']

      entry = FilterEntry(filter_name,
         applyToFrag='no',
         arpOpc='unspecified',
         dFromPort=filter_port,
         dToPort=filter_port,
         etherT='ip',
         prot=filter_protocol,
         sFromPort='unspecified',
         sToPort='unspecified',
         tcpRules='unspecified',
         stateful='1',
         parent=contract)

if __name__ == "__main__":
   main()
