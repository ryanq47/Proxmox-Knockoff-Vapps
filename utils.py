from proxmoxer import ProxmoxAPI
from database import get_credential
from nicegui import ui
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ProxmoxUtils")

# this entire thing probably should have been a class that gets inhereted, but whatever it works


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


def start_multiple_vms(vmid_list, node):
    for vmid in vmid_list:
        start_vm(vmid, node)


def stop_multiple_vms(vmid_list, node):
    for vmid in vmid_list:
        stop_vm(vmid, node)


def restart_multiple_vms(vmid_list, node):
    for vmid in vmid_list:
        restart_vm(vmid, node)


# --------------------------------------
# Delete Ops
# --------------------------------------


def delete_vapp(vmid_list, node, pool_name):
    """
    Deletes VAPP

    Deletes the following specifically, in this order

    1. VM's in Pool
    2. NIC in Pool
    3. Pool itself

    pool_name: PPM_<VAPP_NAME>

    """
    logger.debug("Attmepting to delete VAPP")

    for vmid in vmid_list:
        delete_vm(vmid, node)

    # delete NIC - format it this way. Easiest to do this rather than pass in the NIC
    iface_name = f"{pool_name}_NIC"
    delete_nic(node=node, iface_name=iface_name)

    # delete pool
    delete_pool(pool_name)


def delete_vm(vmid, node):
    """
    Force stop and delete a VM.
    """
    logger.info(f"Attempting to delete VM {vmid} on node {node}")

    proxmox = get_proxmox_class()

    try:
        status = proxmox.nodes(node).qemu(vmid).status.current.get()
        if status.get("status") == "running":
            logger.info(f"VM {vmid} is running. Sending stop command...")
            proxmox.nodes(node).qemu(vmid).status.stop.post()
            logger.info(
                f"Sent stop signal to VM {vmid}, waiting for it to power off..."
            )

            # Wait until VM is off
            import time

            for _ in range(30):  # wait up to ~30s
                time.sleep(1)
                new_status = proxmox.nodes(node).qemu(vmid).status.current.get()
                if new_status.get("status") != "running":
                    break
            else:
                logger.warning(f"VM {vmid} did not shut down in time.")

        ui.notify(f"Deleting VM {vmid}", position="top-right")
        logger.info(f"Deleting VM {vmid}")
        proxmox.nodes(node).qemu(vmid).delete()
        logger.info(f"VM {vmid} deleted successfully")

    except Exception as e:
        logger.error(f"Error deleting VM {vmid}: {e}")


def delete_nic(node, iface_name):
    """
    Deletes a network interface (NIC) from a Proxmox node.

    Args:
        node (str): Node name
        iface_name (str): Name of the NIC to delete (e.g., 'PPM_TEMPLATE_LAB_NIC')
    """
    logger.info(f"Attempting to delete NIC '{iface_name}' on node '{node}'")
    proxmox = get_proxmox_class()

    try:
        proxmox.nodes(node).network(iface_name).delete()
        logger.info(f"Successfully deleted NIC '{iface_name}' on node '{node}'")
        ui.notify(f"Deleted NIC '{iface_name}' on node '{node}'", position="top-right")
    except Exception as e:
        logger.error(f"Error deleting NIC '{iface_name}' on node '{node}': {e}")
        ui.notify(f"Error deleting NIC: {e}", position="top-right", type="warning")


def delete_pool(poolid):
    """
    Deletes a Proxmox resource pool.

    Args:
        poolid (str): The name of the pool to delete.
    """
    logger.info(f"Attempting to delete pool '{poolid}'")
    proxmox = get_proxmox_class()

    try:
        proxmox.pools(poolid).delete()
        logger.info(f"Successfully deleted pool '{poolid}'")
        ui.notify(f"Deleted pool '{poolid}'", position="top-right")
    except Exception as e:
        logger.error(f"Error deleting pool '{poolid}': {e}")
        ui.notify(f"Error deleting pool: {e}", position="top-right", type="warning")


def start_vm(vmid, node):
    logger.info(f"Attempting to start VM {vmid}")
    proxmox = get_proxmox_class()

    ui.notify(f"Starting VM {vmid}", position="top-right")
    logger.info(f"Starting VM {vmid} on node {node}")
    return proxmox.nodes(node).qemu(vmid).status.start.post()


def stop_vm(vmid, node):
    logger.info(f"Attempting to stop VM {vmid}")
    proxmox = get_proxmox_class()

    ui.notify(f"Stopping VM {vmid}", position="top-right")
    logger.info(f"Stopping VM {vmid} on node {node}")
    return proxmox.nodes(node).qemu(vmid).status.shutdown.post()


def restart_vm(vmid, node):
    logger.info(f"Attempting to restart VM {vmid}")
    proxmox = get_proxmox_class()

    ui.notify(f"Restart VM {vmid}", position="top-right")
    logger.info(f"Restart VM {vmid} on node {node}")
    return proxmox.nodes(node).qemu(vmid).status.reboot.post()


def get_vm_status(vmid, node):
    """
    Returns the status of a VM as a string.

    Example return: "running", "stopped", etc.
    """
    logger.info(f"Getting status for VM {vmid} on node {node}")
    proxmox = get_proxmox_class()

    try:
        status = proxmox.nodes(node).qemu(vmid).status.current.get()
        state = status.get("status", "unknown")
        logger.info(f"VM {vmid} status is '{state}'")
        return state
    except Exception as e:
        logger.error(f"Failed to get status for VM {vmid}: {e}")
        return "error"


def get_all_vms_in_pool(pool_name) -> list:
    """
    Returns list of VM id's

    """
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
        # for _node in proxmox.nodes.get():
        #     node_name = _node["node"]
        #     logger.debug(f"Checking node: {_node}")
        #     if node == node_name:
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


def add_existing_bridge_to_vm(vmid, node, bridge_name, model="virtio"):
    """
    Attaches an existing Proxmox bridge to a VM as a new NIC.

    Args:
        vmid (int): ID of the VM
        node (str): Node name
        bridge_name (str): Name of the existing bridge (e.g., "PPM_SOMENAME_NIC")
        model (str): NIC model (default: virtio)
    """
    logger.info(f"Attaching bridge '{bridge_name}' to VM {vmid} on node {node}")
    proxmox = get_proxmox_class()

    try:
        # Determine next available NIC slot (net0, net1, ...)
        config = proxmox.nodes(node).qemu(vmid).config.get()
        nic_index = 0
        while f"net{nic_index}" in config:
            nic_index += 1

        nic_key = f"net{nic_index}"
        nic_value = f"model={model},bridge={bridge_name}"

        proxmox.nodes(node).qemu(vmid).config.post(**{nic_key: nic_value})

        logger.info(
            f"Successfully added '{nic_key}' with bridge '{bridge_name}' to VM {vmid}"
        )
        ui.notify(
            f"NIC {nic_key} connected to '{bridge_name}' added to VM {vmid}",
            position="top-right",
        )

    except Exception as e:
        logger.error(f"Error attaching bridge '{bridge_name}' to VM {vmid}: {e}")
        ui.notify(f"Error adding NIC: {e}", position="top-right", type="warning")


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


def get_valid_templates() -> list:
    """
    Gets all pools in the node, then filters by "PPM_TEMPLATE_"


    reutrns list of valid pool ID's
    """
    logger.info(f"Getting valid vapp templates")
    proxmox = get_proxmox_class()
    pools = proxmox.pools.get()

    pool_id_list = []

    for pool in pools:
        print(pool)
        pool_name = pool.get("poolid")
        if "PPM_TEMPLATE" in pool_name:
            pool_id_list.append(pool_name)

    return pool_id_list


def get_vapps() -> list:
    """
    Gets all the VAPPS, excludes the templates such as "PPM_TEMPLATE"

    reutrns list of pool data
    {poolid:something, sometingelse:?}
    """
    logger.info(f"Getting valid vapp templates")
    proxmox = get_proxmox_class()
    pools = proxmox.pools.get()

    pool_list = []

    for pool in pools:
        print(pool)
        pool_name = pool.get("poolid")
        if "PPM_" in pool_name and "PPM_TEMPLATE" not in pool_name:
            pool_list.append(pool)

    return pool_list


def get_next_available_vmid(minimum=1000):
    proxmox = get_proxmox_class()
    nextid = int(proxmox.cluster.nextid.get())
    if nextid >= minimum:
        return nextid

    # fallback: find next available >= minimum
    used_ids = set()
    for node in proxmox.nodes.get():
        node_name = node["node"]
        for vm in proxmox.nodes(node_name).qemu.get():
            used_ids.add(int(vm["vmid"]))

    candidate = minimum
    while candidate in used_ids:
        candidate += 1

    return candidate


def list_snapshots(vmid, node):
    """
    Returns a list of snapshot names for a given VM.

    Args:
        vmid (int): ID of the VM
        node (str): Node where the VM resides

    Returns:
        List[str]: List of snapshot names
    """
    logger.info(f"Fetching snapshot list for VM {vmid} on node {node}")
    proxmox = get_proxmox_class()
    try:
        snapshots = proxmox.nodes(node).qemu(vmid).snapshot.get()
        snapshot_names = [snap["name"] for snap in snapshots]
        logger.info(f"Found snapshots: {snapshot_names}")
        return snapshot_names
    except Exception as e:
        logger.error(f"Error listing snapshots for VM {vmid}: {e}")
        ui.notify(f"Error listing snapshots: {e}", type="warning", position="top-right")
        return []


def revert_snapshot(vmid, node, snapshot_name):
    """
    Reverts a VM to a given snapshot.

    Args:
        vmid (int): VM ID
        node (str): Node where the VM resides
        snapshot_name (str): The name of the snapshot to revert to
    """
    logger.info(f"Reverting VM {vmid} on node {node} to snapshot '{snapshot_name}'")
    proxmox = get_proxmox_class()
    try:
        proxmox.nodes(node).qemu(vmid).snapshot(snapshot_name).rollback.post()
        ui.notify(
            f"Reverted VM {vmid} to snapshot '{snapshot_name}'", position="top-right"
        )
    except Exception as e:
        logger.error(f"Error reverting VM {vmid} to snapshot '{snapshot_name}': {e}")
        ui.notify(
            f"Error reverting snapshot: {e}", type="warning", position="top-right"
        )


def take_snapshot(vmid, node, snapshot_name, description=""):
    """
    Takes a snapshot of the specified VM.

    Args:
        vmid (int): VM ID
        node (str): Node where the VM resides
        snapshot_name (str): Name of the new snapshot
        description (str): Optional description of the snapshot
    """
    logger.info(f"Creating snapshot '{snapshot_name}' for VM {vmid} on node {node}")
    proxmox = get_proxmox_class()
    try:
        proxmox.nodes(node).qemu(vmid).snapshot.post(
            snapname=snapshot_name,
            description=description,
        )
        logger.info(f"Snapshot '{snapshot_name}' created successfully for VM {vmid}")
        ui.notify(
            f"Snapshot '{snapshot_name}' created for VM {vmid}",
            position="top-right",
        )
    except Exception as e:
        logger.error(f"Error taking snapshot of VM {vmid}: {e}")
        ui.notify(f"Error taking snapshot: {e}", type="warning", position="top-right")
