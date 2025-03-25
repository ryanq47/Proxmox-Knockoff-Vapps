from proxmoxer import ProxmoxAPI
from database import get_credential


def get_proxmox_class():
    # get creds
    url = get_credential("proxmox_url")
    user = get_credential("username")
    password = get_credential("password")

    # get proxmox class
    proxmox_class = ProxmoxAPI(host=url, user=user, password=password, verify_ssl=False)
    return proxmox_class
