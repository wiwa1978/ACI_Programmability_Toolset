from acicontroller import get_token
from acicontroller import execute_rest_call
from create_tenant import create_tenant
from create_vrf import create_vrf
from create_bd import create_bd
import yaml

yml_file = open("./vars/aci_variables.yml").read()
yml_dict = yaml.load(yml_file, yaml.SafeLoader)

tenant = yml_dict['tenant']
vrf = yml_dict['vrf']
bd = yml_dict['bridge_domains'][0]['bd']
bd_subnet = yml_dict['bridge_domains'][0]['gateway'] + "/" + yml_dict['bridge_domains'][0]['mask']

def create_aci_constructs():
   print(f"Creating tenant with name {tenant}")
   response = create_tenant(tenant)

   if not response.status_code == 200:
      print(f"Something went wrong creating the tenant")
   else:
      print(f"Successfully created Tenant with name {tenant}")

   print(f"Creating VRF with name {vrf}")
   response = create_vrf(tenant, vrf)

   if not response.status_code == 200:
      print(f"Something went wrong creating the VRF")
   else:
      print(f"Successfully created VRF with name {vrf}")


   print(f"Creating BD with name {bd}")
   response = create_bd(tenant, vrf, bd, bd_subnet)

   if not response.status_code == 200:
      print(f"Something went wrong creating the BD")
   else:
      print(f"Successfully created BD with name {vrf}")

   print(f"Creating BD {bd}")
   create_bd(tenant, vrf, bd, bd_subnet)

if __name__ == "__main__":
   create_aci_constructs()