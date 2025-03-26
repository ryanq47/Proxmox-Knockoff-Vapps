# Proxmox-Knockoff-Vapps
A Pool Based, Knockoff Vapps control plane for ProxmoxVE. I got tired of not having vapps in Proxmox, so I decided to implement my own. 

Note, this is not a full Vapp implementation, this is just a wrapper around the proxmox API, meant to handle these "Vapps" on one ProxmoxVE instance, using pools & some magic. 

Additionally, this is meant to be PER NODE. I don't have the magic skills to make "Vapps" work accross multiple nodes, so everything is per node. There is a dropdown to switch nodes as well if you are runing a clustered enviornment

## Tool Goals:
 - Easy creation of "Vapps"/VApp templates
    - Select live VM's to add to a "Vapp"

 - Easy Management of "Vapps"
    - Start
    - Stop
    - Restart
    - Revert to snapshot

 - Easy deployment of "Vapps"
    - Management of each VM
    - Clone "Vapp" from "Vapp" Templates


## Running the tool:

#### Install the reqs:
`pip install -r requirements.txt`

#### Run the tool:
`python3 main.py`

#### Navigate to the Web Interface:
The tool listens on `0.0.0.0:8080`. 

`http://127.0.0.1:8080` or `http://<your_ip>:8080`


## Creating VAPPS:

### Creating a new VAPP Tempalte:

If you want to make a new tempalte, ex for a new purpose, follow these steps

Step 1: Create a VAPP Template

Click "Vapp Creator"

1. Optionally, include any pre-existing VM's you want in your VAPP template.

2. Add in the template name

3. click "Create Template" 

4. Start configuring machines to add to your template. Once done, add them to the pool with the name of the vapp template. 

Ex: Add a `kali` box, a firewall, and a Windows DC. Add the created `PPM_<VAPP_NAME>_NIC` NIC to these machines.  

5. Create an instance of the VAPP in the `Templates` section, by entering a name for the VAPP, and hitting `Clone`

On refresh, the VAPP instance should show up in the "Active VAPPs" section


### Spawning a new VAPP:

If you already have a VAPP template, follow these steps to spawn a new instance of it.

1. Create an instance of the VAPP in the `Templates` section, by entering a name for the VAPP, and hitting `Clone`

On refresh, the VAPP instance should show up in the "Active VAPPs" section



#### Resources Created:

NIC: `PPM_<POOLNAME>_NIC`: The NIC created for the VAPP


#### Reccomended:

Ideally, each Vapp would have the follwoing:
 - A FireWall Template (WAN: NIC on said proxmox node, LAN: NIC Created for Vapp)
 
 This allows for multiple labs to exist on one NIC, and is the easiest way to get this rolling. 

Here's an example of a deployed Vapp:

![image](https://github.com/user-attachments/assets/debc45a5-1ef1-473a-9bd0-9e9925ee41bc)

 
## Todo:

- [X] Create Vapp template
- [ ] Create Vapp from template
      - Only include pools that start with "PPM_TEMPLATE"
- [ ] Manage Vapp frmo template (start, stop, snapshot, etc)
      - remove pools that start with "PPM_TEMPLATE"
