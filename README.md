# Proxmox-Knockoff-Vapps
A Pool Based, Knockoff Vapps control plane for ProxmoxVE. I got tired of not having vapps in Proxmox, so I decided to implement my own. 

Note, this is not a full Vapp implementation, this is just a wrapper around the proxmox API, meant to handle these "Vapps" on one ProxmoxVE instance, using pools & some magic. 

Additionally, this is meant to be PER NODE. I don't have the magic skills to make "Vapps" work accross multiple nodes, so everything is per node. There is a dropdown to switch nodes as well if you are runing a clustered enviornment

## Tool Goals:
 - Easy creation of "Vapps"
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

...


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
