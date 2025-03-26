# Proxmox-Knockoff-Vapps

  

A pool-based control plane for ProxmoxVE that mimics "VAPP" functionality. This tool is not a full vApp implementation, but a wrapper around the Proxmox API for managing grouped VM environments on a *per-node* basis.

Again, this is meant to be PER NODE, not for an entire cluster. I don't have the magic skills to make "Vapps" work accross multiple nodes. As a fix, I included a dropdown to switch nodes if you are running multiple/a clustered env, to make the tool somewhat useful in that scenario.

---

  

## Tool Features

  

### VAPP Template Management

- Select existing VMs to build templates

- Automatically clone and convert VMs to templates

- Create dedicated resource pools

  

### VAPP Instance Management

- Clone full environments from templates

- Automatically assign NICs to new VAPPs

- Start, stop, restart, snapshot, and delete entire VAPPs or individual VMs

> Note: Snapshots exist per vm, full VAPP snapshots are not implemented yet

  

---

  

## System Requirements

  

- Python 3.9+

- Proxmox VE API access

- NiceGUI frontend

  

---

  

## Installation & Running

  

```bash

pip  install  -r  requirements.txt

python3  main.py

```

  

Access via: [http://127.0.0.1:8080](http://127.0.0.1:8080) or `http://<your_ip>:8080`

  

---

  

## What This Tool Creates (Automatically)

  

Depending on the action, here’s a breakdown of what this tool does:

  

### When You Create a VAPP Template:

1.  **Clone selected VMs** to create independent copies

2.  **Convert each clone to a VM Template**

3.  **Create a Proxmox Pool**: `PPM_TEMPLATE_<TEMPLATE_NAME>`

4.  **Add all templates to that pool**

  

> Note: NICs are **not** created at template time.

  

---

  

### When You Deploy a VAPP Instance (from Template):

1.  **Create a new Pool**: `PPM_<VAPP_NAME>`

2.  **Create a new NIC**: `PPM_<VAPP_NAME>_NIC`

3.  **Clone every template VM in the selected template pool**

4.  **Add the clones to the new pool**

5.  **Attach the newly created NIC to each cloned VM**

6.  **(Optional)** Start the pool after creation

  

---

  

## Creating a VAPP Template

  

A **VAPP Template** is a reusable stack of configured VMs. You can select live VMs, clone them, and turn them into a template.

  

Alternatively, you can create a template without any VMs, and add in some manually via the Proxox web interface (I'd reccomend this route for more advanced/pre-configured VAPP setups)

  

### Steps

  

1.  **Launch the VAPP Creator**

- From the UI, expand **"Vapp Creator"**

  

2.  **Select VMs to include** (optional)

- These are cloned and turned into templates

  

3.  **Enter a Template Name**

- This becomes `PPM_TEMPLATE_<NAME>`

  

4.  **Click "Create Template"**

- The tool will handle cloning, converting, and pool creation

  

5.  **Post-creation Setup in Proxmox (Manual)**

- Finalize, and/or install additional VMs (install tools, tweak settings)

- Remove all NICs (the tool adds new ones later)

> Note: Don't remove the WAN interface if you have a firewall

- Add any newly created VMs to the pool `PPM_TEMPLATE_<NAME>`

- Convert them to templates via Proxmox GUI

  

---

  

### Recommended Template Configuration

  

To ensure isolation and full control of internal traffic, **you should always include a firewall** VM in your VAPP template.

  

#### Basic Firewall Layout:

  

-  **LAN interface** of the firewall should be connected to the VAPP NIC:

-  `PPM_<TEMPLATE_NAME>_NIC`

-  **WAN interface** can be connected to any other Proxmox bridge:

- e.g., `vmbr0`, `vmbr1`, or a real uplink

  

#### Why This Matters:

  

- Keeps your lab traffic isolated by default

- Allows NAT/firewalling between your VAPP and the outside world

- Gives you visibility and control over all traffic

- Keeps IP's and other internal details consistent

  

---

  

#### Optional: Add Kasm for VDI-style Access

For streamlined browser-based access to your lab machines, it's a good idea to include something like Kasm Workspaces.

  

- Deploy Kasm as a VM inside the VAPP Template

  

- Forward the needed KASM ports to access Kasm externally from the WAN side of the FW.

  

This lets you interact with all your lab systems via a web browser and is handy for VDI-style workflows, remote labs, and shared access.

---

  

## Deploying a New VAPP (From Template)

  

Once you have a template:

  

1. Go to the **Templates** section

2. Enter a name for the new VAPP

3. Click **Clone**

  

The tool will:

- Clone all template VMs

- Create a NIC and Pool for the new instance

- Attach NICs to each VM

- Optionally start the environment

  

---

  

## Managing Active VAPPs

  

From the **Active Pools** section, you can:

  

- View all active VAPPs

- Start/Stop/Restart/Delete entire VAPPs

- Interact with each VM individually

- Take/Revert snapshots on each VM

  

---

  

## Example Workflow: Red Team Lab

  

-  **Template Name:**  `redteam`

-  **VMs:** Kali, Windows DC, pfSense

  

Steps:

- Clone or create VMs

- Convert to templates (in the Proxmox web interface)

- Add to `PPM_TEMPLATE_REDTEAM` (in the Proxmox web interface)

- Deploy with new name (e.g., `RT1`)

  

This gives you a clean, deployable red team lab in one click.

  

---

  

## Tips

  

- This tool is PER-NODE only (cluster support is limited)

- NICs are created **only** during deployment (not at template time)

- VM templates must exist before creating a new VAPP

- Only use **one NIC per VM** unless you understand the networking implications

  

---

  

## Screenshot


Overview of what a deployed lab may look like:

![image](https://github.com/user-attachments/assets/debc45a5-1ef1-473a-9bd0-9e9925ee41bc)

And a visual representation of what happens behind the scenes:

![vapp_creation_visual drawio](https://github.com/user-attachments/assets/feed2b71-245f-499c-851d-e764fb90c3e6)

#### Web GUI:



Templates:
![image](https://github.com/user-attachments/assets/a0c6e444-c416-404e-b174-0024b2a1f441)


Active Vapps:
![image](https://github.com/user-attachments/assets/78b11b5e-fc24-40ad-ba2f-ab1e3f6b0b63)


