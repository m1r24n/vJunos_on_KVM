# list of command
    sudo show runningconfiguration all
    sudo config interface ip remove <Interface_name> <ip_address>
    sudo config interface ip add <interface_name> <ip_address>
    sudo config vlan add <vid>
    sudo config interface ip add Vlan<vid> <ip_address>
    sudo show vlan brief
    sudo show vlan config
    sonic-db-cli CONFIG_DB hget "DEVICE_METADATA|localhost" docker_routing_config_mode


# spit container mode

    "DEVICE_METADATA": {
        "localhost": {
            ...
            "docker_routing_config_mode": "split",
            ...
        }
    },





