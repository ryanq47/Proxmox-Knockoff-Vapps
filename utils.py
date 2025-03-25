from proxmoxer import ProxmoxAPI
from database import get_credential
from nicegui import ui
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ProxmoxUtils")


def get_proxmox_class():
    # logger.info("Fetching Proxmox credentials and initializing API class")
    url = get_credential("proxmox_url")
    user = get_credential("username")
    password = get_credential("password")
    proxmox_class = ProxmoxAPI(host=url, user=user, password=password, verify_ssl=False)
    return proxmox_class


def get_vms_in_pool():
    """
    Would get all VM's in a pool

    """
    logger.info("get_vms_in_pool() called (not yet implemented)")


def get_templates():
    """
    Would get template options

    """
    logger.info("get_templates() called (not yet implemented)")


def start_vm(vmid):
    logger.info(f"Attempting to start VM {vmid}")
    proxmox = get_proxmox_class()
    for node in proxmox.nodes.get():
        node_name = node["node"]
        vms = proxmox.nodes(node_name).qemu.get()
        for vm in vms:
            if vm["vmid"] == vmid:
                ui.notify(f"Starting VM {vmid}", position="top-right")
                logger.info(f"Starting VM {vmid} on node {node_name}")
                return proxmox.nodes(node_name).qemu(vmid).status.start.post()
    logger.error(f"VM with vmid {vmid} not found")
    raise ValueError(f"VM with vmid {vmid} not found")


def stop_vm(vmid):
    logger.info(f"Attempting to stop VM {vmid}")
    proxmox = get_proxmox_class()
    for node in proxmox.nodes.get():
        node_name = node["node"]
        vms = proxmox.nodes(node_name).qemu.get()
        for vm in vms:
            if vm["vmid"] == vmid:
                ui.notify(f"Stopping VM {vmid}", position="top-right")
                logger.info(f"Stopping VM {vmid} on node {node_name}")
                return proxmox.nodes(node_name).qemu(vmid).status.shutdown.post()
    logger.error(f"VM with vmid {vmid} not found")
    raise ValueError(f"VM with vmid {vmid} not found")


def restart_vm(vmid):
    logger.info(f"Attempting to restart VM {vmid}")
    proxmox = get_proxmox_class()
    for node in proxmox.nodes.get():
        node_name = node["node"]
        vms = proxmox.nodes(node_name).qemu.get()
        for vm in vms:
            if vm["vmid"] == vmid:
                ui.notify(f"Restarting VM {vmid}", position="top-right")
                logger.info(f"Restarting VM {vmid} on node {node_name}")
                return proxmox.nodes(node_name).qemu(vmid).status.reset.post()
    logger.error(f"VM with vmid {vmid} not found")
    raise ValueError(f"VM with vmid {vmid} not found")


def get_all_vms_in_pool(pool_name) -> list:
    logger.info(f"Getting all VMs in pool '{pool_name}'")
    vm_id_list = []
    proxmox = get_proxmox_class()
    pool = pool_name
    pool_members = proxmox.pools.get(pool)
    vm_list = [member for member in pool_members["members"] if member["type"] == "qemu"]

    for vm in vm_list:
        vm_id_list.append(vm["vmid"])
        logger.info(f"VMID: {vm['vmid']} on Node: {vm['node']}")

    return vm_id_list


def get_vm_details(vmid):
    logger.info(f"Fetching details for VM {vmid}")
    proxmox = get_proxmox_class()
    for node in proxmox.nodes.get():
        node_name = node["node"]
        vms = proxmox.nodes(node_name).qemu.get()
        for vm in vms:
            if vm["vmid"] == vmid:
                logger.info(f"Found VM {vmid} on node {node_name}")
                return proxmox.nodes(node_name).qemu(vmid).get()


def get_vm_name(vmid):
    logger.info(f"Getting name for VM {vmid}")
    proxmox = get_proxmox_class()
    for node in proxmox.nodes.get():
        node_name = node["node"]
        vms = proxmox.nodes(node_name).qemu.get()
        for vm in vms:
            if vm["vmid"] == vmid:
                name = (
                    proxmox.nodes(node_name).qemu(vmid).config.get().get("name", None)
                )
                logger.info(f"VM {vmid} on node {node_name} is named '{name}'")
                return name


def get_all_vms(node_name):
    logger.info(f"Getting all VMs for node {node_name}")
    proxmox = get_proxmox_class()
    vm_list_of_dicts = proxmox.nodes(node_name).qemu.get()
    logger.info(f"Retrieved {len(vm_list_of_dicts)} VMs")
    return vm_list_of_dicts


def get_all_node_names():
    logger.info("Getting all node names in cluster")
    proxmox = get_proxmox_class()
    node_name_list = []
    for node in proxmox.nodes.get():
        node_name_list.append(node.get("node"))
        logger.info(f"Found node: {node.get('node')}")
    return node_name_list


def create_nic(iface_name, node, type="bridge"):
    logger.info(
        f"Attempting to create NIC '{iface_name}' on node '{node}' (type: {type})"
    )
    proxmox = get_proxmox_class()
    try:
        for _node in proxmox.nodes.get():
            node_name = _node["node"]
            logger.debug(f"Checking node: {_node}")
            if node == node_name:
                ui.notify(
                    f"Creating NIC: Node: {node}, interface name:{iface_name} Type:{type} ",
                    position="top-right",
                )
                proxmox.nodes(node).network.post(iface=iface_name, node=node, type=type)
                logger.info(f"NIC '{iface_name}' successfully created on {node}")
                ui.notify(
                    f"NIC {iface_name} created successfully on {node}",
                    position="top-right",
                )
    except Exception as e:
        logger.error(f"Error creating NIC {iface_name} on node {node}: {e}")
        ui.notify(f"Error creating NIC: {e}", position="top-right", type="warning")


def create_pool(poolid: str):
    logger.info(f"Attempting to create pool '{poolid}'")
    proxmox = get_proxmox_class()
    try:
        proxmox.pools.post(poolid=poolid)
        logger.info(f"Successfully created pool '{poolid}'")
        ui.notify(f"Created pool {poolid}", position="top-right")
    except Exception as e:
        logger.error(f"Error creating pool '{poolid}': {e}")
        ui.notify(f"Error creating POOL: {e}", position="top-right", type="warning")


def clone_host(new_id, node, vmid_of_host_to_clone):
    logger.info(f"Cloning VM {vmid_of_host_to_clone} -> {new_id} on node {node}")
    proxmox = get_proxmox_class()
    try:
        proxmox.nodes(node).qemu(vmid_of_host_to_clone).clone().post(newid=new_id)
        logger.info(f"Cloned host {vmid_of_host_to_clone} -> {new_id}")
        ui.notify(
            f"Cloned host {vmid_of_host_to_clone} -> {new_id}", position="top-right"
        )
    except Exception as e:
        logger.error(f"Error cloning VM {vmid_of_host_to_clone}: {e}")
        ui.notify(f"Error cloning host: {e}", position="top-right", type="warning")


def add_host_to_pool(poolid, vmid):
    logger.info(f"Adding VM {vmid} to pool '{poolid}'")
    proxmox = get_proxmox_class()
    try:
        proxmox.pools(poolid).put(vms=str(vmid))
        logger.info(f"VM {vmid} added to pool '{poolid}'")
        ui.notify(f"Added host {vmid} to pool '{poolid}'", position="top-right")
    except Exception as e:
        logger.error(f"Error adding VM {vmid} to pool '{poolid}': {e}")
        ui.notify(f"Error adding to pool: {e}", position="top-right", type="warning")


def convert_to_template(vmid, node):
    logger.info(f"Converting VM {vmid} on node {node} to template")
    proxmox = get_proxmox_class()
    try:
        proxmox.nodes(node).qemu(vmid).template().post()
        logger.info(f"VM {vmid} successfully converted to template")
        ui.notify(f"Converted host {vmid} to template", position="top-right")
    except Exception as e:
        logger.error(f"Error converting VM {vmid} to template: {e}")
        ui.notify(
            f"Error converting to template: {e}", position="top-right", type="warning"
        )


import time


def wait_for_unlock(vmid, node, timeout=60):
    logger.info(f"Waiting for VM {vmid} on node {node} to unlock (timeout {timeout}s)")
    proxmox = get_proxmox_class()
    start = time.time()

    while time.time() - start < timeout:
        status = proxmox.nodes(node).qemu(vmid).status.current.get()
        if "lock" not in status:
            logger.info(f"VM {vmid} is now unlocked")
            return
        ui.notify(f"Host {vmid} is in lock... waiting for unlock", position="top-right")
        logger.debug(f"VM {vmid} is locked: {status.get('lock')}")
        time.sleep(1)

    logger.error(f"Timeout: VM {vmid} is still locked after {timeout} seconds")
    raise TimeoutError(f"VM {vmid} is still locked after {timeout} seconds.")
