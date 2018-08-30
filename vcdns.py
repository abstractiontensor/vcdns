#!/usr/bin/env python3

from pyVim import connect
from pyVmomi import vim

import yaml
import sys
import ipaddress


CONFIG_PATH = 'config.yml'
# Parsing arguments
def confpath_argv():
    """
    Parses argv, loades config.yml
    :return: config path
    """
    if len(sys.argv) == 1:
        return CONFIG_PATH
    if len(sys.argv) == 3 and sys.argv[2] == '-c':
        return sys.argv[3]
    return None

def initConf(confpath):
    """
    :param confpath - YAML configuration path
    Loades YAML config
    :return: Configuration tree
    """
    return yaml.load(open(confpath))


def main():
    config = initConf(confpath_argv())
    vcc = connect.SmartConnectNoSSL(host=config['Connection']['host'],
                                    user=config['Connection']['user'],
                                    pwd=config['Connection']['pswd'],
                                    port=config['Connection']['port'])

    containerView = vcc.content.viewManager.CreateContainerView(
        vcc.content.rootFolder,
        [vim.VirtualMachine],
        recursive=True
    )
    resolv=[]
    for vm in containerView.view:
        try:
            for net in vm.guest.net:
                if ipaddress.IPv4Address(net.ipAddress[0]):
                    resolv.append(
                        [net.ipAddress[0],
                         vm.guest.ipStack[0].dnsConfig.hostName]
                    )
        except:
            continue

    # Print bindings to stdout
    if config['Debug']['enabled']:
        for entry in resolv:
            print(entry[0].ljust(20) + entry[1])

    # Populating hosts file
    if config['Hosts']['enabled']:
        hostsfile = open(file=config['Hosts']['path'], mode='w')
        hostsfile.write('127.0.0.1           localhost\n')
        for entry in resolv:
            hostsfile.write(entry[0].ljust(20) + entry[1] + "\n")
        hostsfile.close()


if __name__ == '__main__':
    main()
