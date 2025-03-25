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


def create_pool(poolid: str):
    """
    Creates a pool

    poolid (str): A name for the pool
    """

    proxmox = get_proxmox_class()

    try:
        proxmox.pools.post(poolid=poolid)
        ui.notify(f"Created pool {poolid}", position="top-right")
    except Exception as e:
        ui.notify(f"Error creating POOL: {e}", position="top-right", type="warning")


def clone_host(new_id, node, vmid_of_host_to_clone):
    """
    Clones a VM to a new VM ID.

    new_id (int): New VM ID
    node (str): Node name
    vmid_of_host_to_clone (int): Existing VM ID to clone
    """
    proxmox = get_proxmox_class()

    try:
        proxmox.nodes(node).qemu(vmid_of_host_to_clone).clone().post(newid=new_id)
        ui.notify(
            f"Cloned host {vmid_of_host_to_clone} -> {new_id}", position="top-right"
        )
    except Exception as e:
        ui.notify(f"Error cloning host: {e}", position="top-right", type="warning")


def add_host_to_pool(poolid, vmid):
    """
    Adds a VM to an existing Proxmox pool using PUT /pools/{poolid}
    """
    proxmox = get_proxmox_class()
    try:
        proxmox.pools(poolid).put(vms=str(vmid))
        ui.notify(f"Added host {vmid} to pool '{poolid}'", position="top-right")
    except Exception as e:
        ui.notify(f"Error adding to pool: {e}", position="top-right", type="warning")


def convert_to_template(vmid, node):
    """
    Converts a VM into a template.

    vmid (int): VM ID to convert
    node (str): Node where the VM resides
    """
    proxmox = get_proxmox_class()

    try:
        proxmox.nodes(node).qemu(vmid).template().post()
        ui.notify(f"Converted host {vmid} to template", position="top-right")
    except Exception as e:
        ui.notify(
            f"Error converting to template: {e}", position="top-right", type="warning"
        )


import time


def wait_for_unlock(vmid, node, timeout=60):
    """
    Waits until the specified VM is no longer locked.
    """
    proxmox = get_proxmox_class()
    start = time.time()

    while time.time() - start < timeout:
        status = proxmox.nodes(node).qemu(vmid).status.current.get()
        if "lock" not in status:
            return
        ui.notify(f"Host {vmid} is in lock... waiting for unlock", position="top-right")
        time.sleep(1)

    raise TimeoutError(f"VM {vmid} is still locked after {timeout} seconds.")
