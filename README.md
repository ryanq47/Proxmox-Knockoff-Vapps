# Proxmox-Knockoff-Vapps

A Pool Based, Knockoff Vapps control plane for ProxmoxVE. I got tired of not having vapps in Proxmox, so I decided to implement my own.

  

Note, this is not a full Vapp implementation, this is just a wrapper around the proxmox API, meant to handle these "Vapps" on one ProxmoxVE instance, using pools & some magic. 

  

Additionally, this is meant to be PER NODE. I don't have the magic skills to make "Vapps" work accross multiple nodes, so everything is per node. There is a dropdown to switch nodes as well if you are runing a clustered enviornment
  

## Tool Goals:

- Easy creation of VAPP /VApp templates

	- Select live VM's to add to a VAPP  template

  
- Easy Management of VAPP 

	- Start

	- Stop

	- Restart
  

- Easy deployment of VAPP 

	- Management of each VM

	- Create VAPP instances from VAPP  Templates

  
  

## Running the tool:

  

#### Install the reqs:

`pip install -r requirements.txt`

  

#### Run the tool:

`python3 main.py`

  

#### Navigate to the Web Interface:

The tool listens on `0.0.0.0:8080`.

  

`http://127.0.0.1:8080` or `http://<your_ip>:8080`

  
  

Absolutely, here’s a cleaner, clearer version of your VAPP template creation guide — rewritten for clarity, structure, and flow, while retaining all the key steps and context from your current setup.

----------

## Creating a VAPP Template

A **VAPP Template** is a pre-configured group of VMs, NIC's, and settings that can be cloned and reused to rapidly spin up consistent lab environments.

###  Step-by-Step: Create a New VAPP Template

----------

### **Step 1: Launch the VAPP Creator**

1.  Open the **Proxmox Pools Manager** web interface.
    
2.  Click the **"Vapp Creator"** section to expand it.
    

----------

### **Step 2: Select Base VMs (Optional)**

-   If you have existing VMs you'd like to include in the template (e.g., Kali, Windows, Firewall, etc.), select them from the VM table.
    
-   These machines will be cloned as a starting point for your template.
    

----------

### **Step 3: Enter a Template Name**

-   Enter a **name** for the VAPP template (e.g., `ad_lab`, `pentest_stack`).
    
-   This name will be used to:
    
    -   Create a **dedicated NIC**: `PPM_<TEMPLATE_NAME>_NIC`
        
    -   Create a **resource pool**: `PPM_TEMPLATE_<TEMPLATE_NAME>`
        

----------

### **Step 4: Click "Create Template"**

-   This triggers the following actions automatically:
    
    1.  Clones the selected VMs (if any)
        
    2.  Converts those clones into templates
        
    3.  Creates a NIC named `PPM_<TEMPLATE_NAME>_NIC`
        
    4.  Creates a Proxmox pool named `PPM_TEMPLATE_<TEMPLATE_NAME>`
        
    5.  Adds the cloned templates to the pool
        

----------

### **Step 5: Configure the Template VMs (In Proxmox)**

After the system creates the base template pool, switch over to **Proxmox** and complete the setup:

1.  **Start and configure each VM** as needed:
    
    -   Set up users, network settings, or services.
        
    -   Add tools or configurations specific to the lab purpose.
        
2.  **Attach the VAPP NIC**:
    
    -   Add `PPM_<TEMPLATE_NAME>_NIC` to each VM you want networked together.
        
3.  **Add Final VMs to the Template Pool**:
    
    -   Make sure every VM you want in the final template is added to:
        
        -   `PPM_TEMPLATE_<TEMPLATE_NAME>`
            

----------
### Recommended Template Configuration

To ensure isolation and full control of internal traffic, **you should always include a firewall** VM in your VAPP template.

#### Basic Firewall Layout:

-   **LAN interface** of the firewall should be connected to the VAPP NIC:
    
    -   `PPM_<TEMPLATE_NAME>_NIC`
        
-   **WAN interface** can be connected to any other Proxmox bridge:
    
    -   e.g., `vmbr0`, `vmbr1`, or a real uplink
        

####  Why This Matters:

-   Keeps your lab traffic isolated by default
    
-   Allows NAT/firewalling between your VAPP and the outside world
    
-   Gives you visibility and control over all traffic
- Keeps IP's and other internal details consistent

---

### Example:

You're building a red team lab:

-   Template name: `redteam`
    
-   VMs to include: Kali, pfSense, Windows Server (DC)
    

**Steps:**

-   Create VAPP template named `redteam`
    
-   Clone a base Kali box, firewall, and DC if desired
	- Or just create a new VM for each
    
-   Configure them in Proxmox
    
-   Attach `PPM_REDTEAM_NIC` to the **LAN side** of the firewall

-   Attach the **WAN side** of the firewall to `vmbr0`
    
-   Add all machines to the pool `PPM_TEMPLATE_REDTEAM`
    

You're done — this is now your reusable, isolated red team lab template.

----------


### Spawning a new VAPP:

  

If you already have a VAPP template, follow these steps to spawn a new instance of it.

  

1. Create an instance of the VAPP in the `Templates` section, by entering a name for the VAPP, and hitting `Clone`

  

On refresh, the VAPP instance should show up in the "Active VAPPs" section

  
  
  

#### Resources Created:

  

NIC: `PPM_<POOLNAME>_NIC`: The NIC created for the VAPP
Pool: `PPM_<TEMPLATE_NAME>`  : The pool created to hold the VM's
  
  

#### Reccomended:

 

Here's an example of a deployed Vapp:

  

![image](https://github.com/user-attachments/assets/debc45a5-1ef1-473a-9bd0-9e9925ee41bc)

  
