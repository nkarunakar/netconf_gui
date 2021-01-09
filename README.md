 # NETCONF GUI tool for ncclient NETCONF operations.

 ##### NETCONF_GUI tool provides a PyQt5 based GUI interface to connnect to NETCONF supported device.
 ##### NETCONG GUI tool uses ncclient library to perform all NETCONF operations.
 
 ---
 
 ## Description:
 
 NETCONF GUI tool connects to any NETCONF supported device & downloads YANG files for processing or parsing.
 In case yangs are already available with the user, user can specify the directory in the GUI to process/parse the YANG files.
 
 Based on processing, the tool automatically identifies YANGS that support GET/GETCONFIG/ACTION RPC calls & lists the filtered supported YANGS in dropdown menu for user to perform NETCONF operations.
 
 **NETCONF GUI tool automatically generated input XML files, based on parsing each YANG file to identify namespaces, prefixes & containers, for GET/GETCONFIG operations based on YANG/Capability selected by user from dropdown menu & displays output to user.**
 
 If desired, User also has option to enter custom XML as input.
 
 ---
 
 ## Details on operations supported.
 
 1. Connect to NETCONF device.
 2. Download YANGs from device to your disk. **(via ncclient getschema)*
 3. Automatically parse downloaded yangs to create GET/GETCONFIG input XMLs. *(via ncclient get/getconfig)*
 4. Perform GET/GETCONFIG operations for user selected YANG using auto generated input XML specific to selected yang.  *(via ncclient get/getconfig)*
 5. Perform GET/GETCONFIG operations for custom XML input specified by user. *(via ncclient get/getconfig)*
 
	**All GET/GETCONFIG operations results, if successful, will be saved in disk as XML file under working directory.**
	**Output will also be shown in GUI in read-only text box "Output"**

 6. If supported by ynag definition, user can perform RPC ACTIONS for selected YANG. *(via ncclient dispatch module)*
 
 ---

 ## Usage:

 Launch NCGUI using below command:

 ```C:\NCGUI>python main.py```

 In the NCGUI enter Device IP address, username, password & click on "Connect"

 Once connection is successful, below GUI is displayed to user.

C1

 User can click on "LOAD YANGS" to download yangs to default working directory.

C2

 **User can specify non-default folder by disabling "Use default" checkbox.**

 Once download is successful, below message is shown to user.

C3

 If any error, same will be reported. YANGS download from device to disk follows a "Best Effort" approach.

 Click on "DO OPERATIONS" to trigger yang processing & resulting "YangDetails" GUI.
 **User can specify non-default folder containing all YANG files that needs to be processed by disabling "Use default" checkbox.**


C4

 YangDetails GUI contains supports below operations.

C5

 Enable "Use filtered yangs for get/getconfig" checkbox to support below operations. (Enabled by default: Recommended)

* *GET* -> Perfors GET operation for selected yang.

* **GETCONFIG** -> Perfors GET operation for selected yang.
	
* **ACTION** -> When enabled, supports RPC ACTION calls for selected yang.

* **CLEAR SCREEN** -> Clears Output screen.
	
* **CUSTOM GET/GETCONFIG** -> Launcher Input window for user's custom XML input.
			
	C7
	

* **CLOSE** -> Closed "YangDetails" GUI
	
 Select desired YANG file from available dropdown menu.

C6



 Once YANG is selected click on GET/GETCONFIG/ACTION buttons for desired operation.
 Output will be shown in Output text box & also downloaded onto working directory as XML file.

 A Sample success message is as below:

C8

 ---


## Future improvements:

* Support for EDITCONFIG

* More Robust RPC calls support.

* Add logging to track operations.

