#!/usr/bin/env python3
import apstra_api
import yaml
# main program

asn="""
items:
- name: ASN_Spine
  first: 65001
  last: 65009
- name: ASN_Leaf
  first: 65011
  last: 65019
"""
asn_dict = yaml.load(asn,Loader=yaml.FullLoader)
for i in asn_dict['items']:
    print(f"creating pool {i['name']}")
    apstra_api.create_asn_pools(i)

ippools="""
items:
- name: Fabric_link
  subnets:
  - network: 10.101.0.0/24
- name: Loopback_Spine
  subnets:
  - network: 10.101.1.0/24
- name: Loopback_Leaf
  subnets:
  - network: 10.101.2.0/24
- name: Loopback_VRF
  subnets:
  - network: 10.101.3.0/24
"""
ippools_dict = yaml.load(ippools,Loader=yaml.FullLoader)
for i in ippools_dict['items']:
    print(f"creating ip pool {i['name']}")
    apstra_api.create_ip_pools(i)


ippools="""
items:
- name: Loopback_Spine
  subnets:
  - network: fc00:dead:beef:101::/64
- name: Loopback_Leaf
  subnets:
  - network: fc00:dead:beef:102::/64
- name: Loopback_VRF
  subnets:
  - network: fc00:dead:beef:103::/64
"""
ippools_dict = yaml.load(ippools,Loader=yaml.FullLoader)
for i in ippools_dict['items']:
    print(f"creating ip pool {i['name']}")
    apstra_api.create_ipv6_pools(i)

# ld="""
# items:
# - display_name: vEX_Spine
#   panels:
#   - panel_layout:
#       column_count: 10
#       row_count: 1
#     port_groups:
#     - count: 10
#       roles:
#       - superspine
#       - unused
#       - leaf
#       - generic
#       speed:
#         unit: G
#         value: 1
#     port_indexing:
#       order: T-B, L-R
#       schema: absolute
#       start_index: 1
# - display_name: vEX_Leaf
#   panels:
#   - panel_layout:
#       column_count: 10
#       row_count: 1
#     port_groups:
#     - count: 2
#       roles:
#       - spine
#       speed:
#         unit: G
#         value: 1
#     - count: 8
#       roles:
#       - unused
#       - generic
#       - access
#       speed:
#         unit: G
#         value: 1
#     port_indexing:
#       order: T-B, L-R
#       schema: absolute
#       start_index: 1
# - display_name: vEX_Collapsed
#   panels:
#   - panel_layout:
#       column_count: 10
#       row_count: 1
#     port_groups:
#     - count: 10
#       roles:
#       - superspine
#       - unused
#       - leaf
#       - generic
#       - peer
#       - access
#       - spine
#       speed:
#         unit: G
#         value: 1
#     port_indexing:
#       order: T-B, L-R
#       schema: absolute
#       start_index: 1
# """
# - display_name: vEVO_Spine
#   panels:
#   - panel_layout:
#       column_count: 12
#       row_count: 1
#     port_groups:
#     - count: 12
#       roles:
#       - superspine
#       - leaf
#       - generic
#       speed:
#         unit: G
#         value: 10
#     port_indexing:
#       order: T-B, L-R
#       schema: absolute
#       start_index: 1
# """

# ld_dict = yaml.load(ld,Loader=yaml.FullLoader)
# for i in ld_dict['items']:
#   apstra_api.create_logical_devices(i)
