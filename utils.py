from proxmoxer import ProxmoxAPI
from database import get_credential
from nicegui import ui


def get_proxmox_class():
    # get creds
    url = get_credential("proxmox_url")
    user = get_credential("username")
    password = get_credential("password")

    # get proxmox class
    proxmox_class = ProxmoxAPI(host=url, user=user, password=password, verify_ssl=False)
    return proxmox_class


def get_vms_in_pool():
    """
    Would get all VM's in a pool

    """


def get_templates():
    """
    Would get template options

    """


def start_vm(vmid):
    """
    Start a VM given its vmid using the proxmoxer instance.
    Searches for the VM across all nodes and calls the start endpoint.
    """
    proxmox = get_proxmox_class()
    for node in proxmox.nodes.get():
        node_name = node["node"]
        vms = proxmox.nodes(node_name).qemu.get()
        for vm in vms:
            if vm["vmid"] == vmid:
                # Issue the start command for the found VM.
                ui.notify(f"Starting VM {vmid}", position="top-right")
                return proxmox.nodes(node_name).qemu(vmid).status.start.post()
    raise ValueError(f"VM with vmid {vmid} not found")


def stop_vm(vmid):
    """
    Stop (gracefully shutdown) a VM given its vmid using the proxmoxer instance.
    Searches for the VM across all nodes and calls the shutdown endpoint.
    """
    proxmox = get_proxmox_class()
    for node in proxmox.nodes.get():
        node_name = node["node"]
        vms = proxmox.nodes(node_name).qemu.get()
        for vm in vms:
            if vm["vmid"] == vmid:
                ui.notify(f"Stopping VM {vmid}", position="top-right")
                # Issue the shutdown command for the found VM.
                return proxmox.nodes(node_name).qemu(vmid).status.shutdown.post()
    raise ValueError(f"VM with vmid {vmid} not found")


def restart_vm(vmid):
    """
    Restart a VM given its vmid using the proxmoxer instance.
    Searches for the VM across all nodes and calls the reset endpoint to force a restart.
    """
    proxmox = get_proxmox_class()
    for node in proxmox.nodes.get():
        node_name = node["node"]
        vms = proxmox.nodes(node_name).qemu.get()
        for vm in vms:
            if vm["vmid"] == vmid:
                ui.notify(f"Restarting VM {vmid}", position="top-right")
                # Issue the reset command for the found VM.
                return proxmox.nodes(node_name).qemu(vmid).status.reset.post()
    raise ValueError(f"VM with vmid {vmid} not found")


def get_all_vms_in_pool(pool_name) -> list:
    """
    Gets all the VM's in a pool

    pool_name: The name of the pool

    """
    vm_id_list = []

    proxmox = get_proxmox_class()
    # Specify the pool name you're interested in
    pool = pool_name

    # Get members of the pool
    pool_members = proxmox.pools.get(pool)

    # Filter only VMs (type 'qemu' for virtual machines)
    vm_list = [member for member in pool_members["members"] if member["type"] == "qemu"]

    # Print VM IDs and Node names
    for vm in vm_list:
        vm_id_list.append(vm["vmid"])
        print(f"VMID: {vm['vmid']} on Node: {vm['node']}")

    return vm_id_list


def get_vm_details(vmid):
    """
    Gets VM details, general call to /nodes/<node>/qemu


    """
    proxmox = get_proxmox_class()
    for node in proxmox.nodes.get():
        node_name = node["node"]
        vms = proxmox.nodes(node_name).qemu.get()
        for vm in vms:
            if vm["vmid"] == vmid:
                # ui.notify(f"Reseting VM {vmid}", position="top-right")
                # Issue the reset command for the found VM.
                # return proxmox.nodes(node_name).qemu(vmid).status.reset.post()
                return proxmox.nodes(node_name).qemu(vmid).get()


def get_vm_name(vmid):
    """
    Gets VM details, general call to /nodes/<node>/qemu


    """
    proxmox = get_proxmox_class()
    for node in proxmox.nodes.get():
        node_name = node["node"]
        vms = proxmox.nodes(node_name).qemu.get()
        for vm in vms:
            if vm["vmid"] == vmid:
                # ui.notify(f"Reseting VM {vmid}", position="top-right")
                # config endpoint has all the details
                return (
                    proxmox.nodes(node_name).qemu(vmid).config.get().get("name", None)
                )


def get_all_vms(node_name):
    """
    Gets VM details, general call to /nodes/<node>/qemu

    """
    proxmox = get_proxmox_class()
    vm_list_of_dicts = proxmox.nodes(node_name).qemu.get()
    # print(vms)
    return vm_list_of_dicts


def get_all_node_names():
    """
    Gets all node names in the proxmox cluster
    """
    proxmox = get_proxmox_class()

    node_name_list = []
    for node in proxmox.nodes.get():
        # toss name into list
        node_name_list.append(node.get("node"))

    return node_name_list


def create_nic(iface_name, node, type="bridge"):
    """
    Creates a NIC
    """
    proxmox = get_proxmox_class()
    try:

        for _node in proxmox.nodes.get():
            print(_node)
            node_name = _node["node"]
            if node == node_name:
                # create nic
                ui.notify(
                    f"Creating NIC: Node: {node}, interface name:{iface_name} Type:{type} ",
                    position="top-right",
                )
                proxmox.nodes(node).network.post(iface=iface_name, node=node, type=type)
                ui.notify(
                    f"NIC {iface_name} created successfully on {node}",
                    position="top-right",
                )

            # vm_list_of_dicts = proxmox.nodes(node_name).qemu.get()
    except Exception as e:
        ui.notify(f"Error creating NIC: {e}", position="top-right", type="warning")
