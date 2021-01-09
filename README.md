 # NETCONF GUI tool for ncclient NETCONF operations.

 ##### NETCONF_GUI tool provides a PyQt5 based GUI interface to connnect to NETCONF supported device.
 ##### NETCONF GUI tool uses ncclient library to perform all NETCONF operations.
 
 ---
 
 ## Requirements:
 
 Python==3.8.5
 
 PyQt5
 
 ncclient==0.6.7
 
 lxml==4.5.2
 
 
 ---
 
 
 ## Description:
 
 NETCONF GUI tool connects to any NETCONF supported device & downloads YANG files for processing or parsing.
 In case yangs are already available with the user, user can specify the directory housing the yang files in the GUI to process/parse the YANG files.
 
 Based on processing, the tool automatically identifies YANGS that support GET/GETCONFIG/ACTION RPC calls & lists the filtered supported YANGS in dropdown menu for user to perform NETCONF operations.
 
 **NETCONF GUI tool automatically generated input XML files, based on parsing each YANG file to identify namespaces, prefixes & containers, for GET/GETCONFIG operations based on YANG/Capability selected by user from dropdown menu & displays output to user.**
 
 **Supported on Python 3 only.**
 
 If desired, User also has the option to enter custom XML as input.
 
 ---
 
 ## Details on operations supported.
 
 1. Connect to NETCONF device.
 2. Download YANGs from device to your disk. *(via ncclient getschema)*
 3. Automatically parse downloaded yangs to create GET/GETCONFIG input XMLs. *(via ncclient get/getconfig)*
 4. Perform GET/GETCONFIG operations for user selected YANG using auto generated input XML specific to selected yang.  *(via ncclient get/getconfig)*
 5. Perform GET/GETCONFIG operations for custom XML input specified by user. *(via ncclient get/getconfig)*
 
	**All GET/GETCONFIG operations results, if successful, will be saved in disk as XML file under working directory.**
	**Output will also be shown in GUI in read-only text box "Output"**

 6. If supported by yang definition, user can perform RPC ACTIONS for selected YANG. *(via ncclient dispatch module)*
 
 ---

 ## Usage:

 Launch NCGUI using below command:

 ```C:\NCGUI>python main.py```

 In NCGUI enter Device IP address, username, password, NETCONF port *(defaults to 830)* & click on "Connect"

 Once connection is successful, below GUI is displayed to user.

![ConnectionSuccess](https://user-images.githubusercontent.com/72927429/104090110-6356b480-529a-11eb-9df7-38561e380c91.PNG)


 User can click on "LOAD YANGS" to download yangs to default working directory.

![LoadYangs](https://user-images.githubusercontent.com/72927429/104090111-63ef4b00-529a-11eb-9a02-71c8c33396c8.PNG)

 
 **User can specify non-default folder by disabling "Use default" checkbox.**

 Once download is successful, below message is shown to user.

![DownloadSuccess](https://user-images.githubusercontent.com/72927429/104090112-6487e180-529a-11eb-9643-df5407c51d12.PNG)

 
 If any error, same will be reported. YANGS download from device to disk follows a "Best Effort" approach.

 Click on "DO OPERATIONS" to trigger yang processing & resulting "YangDetails" GUI.
 **User can specify non-default folder containing all YANG files that needs to be processed by disabling "Use default" checkbox.**

![DoOperations](https://user-images.githubusercontent.com/72927429/104090113-65207800-529a-11eb-9780-25b4732b8af7.PNG)

 YangDetails GUI contains/supports below operations.

![YangDetails](https://user-images.githubusercontent.com/72927429/104090114-65b90e80-529a-11eb-99ae-653bacc52f0e.PNG)


 Enable "Use filtered yangs for get/getconfig" checkbox to support below operations. **(Enabled by default: Recommended)**

* **GET** -> Performs GET operation for selected yang.

* **GETCONFIG** -> Performs GET operation for selected yang.
	
* **ACTION** -> When enabled, supports RPC ACTION calls for selected yang.

* **CLEAR SCREEN** -> Clears Output screen.
	
* **CUSTOM GET/GETCONFIG** -> Launches Input window for user's custom XML input.

![CustomXML](https://user-images.githubusercontent.com/72927429/104090108-62be1e00-529a-11eb-97d0-b947b1c5cd57.PNG)
			
	

* **CLOSE** -> Closes "YangDetails" GUI

	
 Select desired YANG file from available dropdown menu.

![DropDown](https://user-images.githubusercontent.com/72927429/104090107-618cf100-529a-11eb-9189-56cd758b10a4.PNG)



 Once YANG is selected click on GET/GETCONFIG/ACTION buttons for desired operation.
 Output will be shown in Output text box & also downloaded onto working directory as XML file.

 A Sample success message, with details on downloaded XML response, is as below:

![SampleSuccess](https://user-images.githubusercontent.com/72927429/104090109-62be1e00-529a-11eb-9013-c14fee55c849.PNG)

 ---


## Future improvements:

* Support for EDITCONFIG

* More Robust RPC calls support.

* Add logging to track operations.

