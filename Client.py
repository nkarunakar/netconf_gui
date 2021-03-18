import sys, os, warnings, re, time, argparse, traceback, logging
warnings.simplefilter("ignore", DeprecationWarning)
from ncclient import manager
from lxml import etree
from ncclient.operations.errors import OperationError, TimeoutExpiredError, MissingCapabilityError
from ncclient.operations.rpc import RPCError
from YangParser import YangParser
from ncclient.xml_ import new_ele, sub_ele, new_ele_ns,sub_ele_ns,to_ele,to_xml

class Client:
    def __init__(self,ipaddress,username,password,portnum=830):
        modulere = re.compile(".*module=(.*?)&")
        modulere2 = re.compile(".*module=(.*)")
        self.__yprops = {}
        self.__deviceip=ipaddress
        self.__devusername=username
        self.__devpassword=password
        self.__ncport=portnum
        self.__ypath=os.path.join(os.getcwd(),self.__deviceip)
        self.__myyangs=[]
        self.__allcaps=[]
        self.__actiontag=None
        self.__prefixtonamespace = {}
        self.__mydevice = manager.connect(host=self.__deviceip,
                                          port=self.__ncport,
                                          username=self.__devusername,
                                          password=self.__devpassword,
                                          hostkey_verify=False,
                                          manager_params={'timeout': 600})
        for c in self.__mydevice.server_capabilities:
            self.__allcaps.append(c)
            if modulere.match(c):
                self.__myyangs.append(modulere.search(c).group(1))
            elif modulere2.match(c):
                self.__myyangs.append(modulere2.search(c).group(1))
            elif c.find("actions") > 0:
                self.__actiontag=c
        #if self.__actiontag is None:
            #self.__actiontag="urn:ietf:params:netconf:base:1.1"'''
        self.__myyangs.sort()
        #self.__actiontag = "urn:ietf:params:netconf:base:1.1"

    @property
    def getMyAtag(self):
        return self.__actiontag

    @property
    def getMyIP(self):
        return self.__deviceip

    @property
    def getDefaultYPath(self):
        return self.__ypath

    def disconnect(self):
        self.__mydevice.close_session()

    def printcap(self):
        for entry in self.__allcaps:
            yield entry

    def returnRPCOpenBlock(self,ykey):
        RPCCONTENT = "<action xmlns=\"" + self.__actiontag + "\">\n<data>\n"
        RPCCONTENT = RPCCONTENT + "<" + self.__yprops[ykey].getprefix + " xmlns=\"" + self.__yprops[ykey].getnamespace + "\">"
        return RPCCONTENT

    def returnRPCCloseBlock(self,ykey):
        RPCCONTENT = "\n</" + self.__yprops[ykey].getprefix + ">" + "\n</data>\n</action>"
        return RPCCONTENT
        #RPCCONTENT = CONTENT + "<" + self.__yprops[ykey].getprefix + " xmlns=\"" + self.__yprops[ykey].getnamespace + "\">\n"

    @property
    def printMyYangs(self):
        return self.__myyangs
    #def getAllYangs(self,DeviceObj)

    def printCapabilities(self):
        for x in self.__mydevice.server_capabilities:
            yield x

    def printAllRPCCalls(self):
        for key in self.__yprops.keys():
            if self.__yprops[key].ifRPCSupported:
                self.__yprops[key].printRPCValues()

    def printRPCNames(self,ykey):
        if self.__yprops[ykey].ifRPCSupported:
            for name in self.__yprops[ykey].printRPCs():
                yield name
                
    def getAugStatus(self,ykey):
        return self.__yprops[ykey].getaugmentstatus

    def getAllAugLeafs(self,ykey):
        tempdict=self.__yprops[ykey].returnAugs()
        for c in tempdict.keys():
            for c1 in tempdict[c]["leafs"]:
                value=c+":"+c1
                yield value

    def getAllUses(self,ykey):
        temparray=self.__yprops[ykey].returnUses()
        for c in temparray:
            yield c

    def parseyangforRPCs(self,ykey):
        self.__yprops[ykey].parseRPCYang()

    def printLeafsforRPC(self,ykey,rpccall):
        return self.__yprops[ykey].returnLeafs(rpccall)

    def getLeafPropsforRPC(self,ykey,rpccall,leaf):
        return self.__yprops[ykey].returnLeafProps(rpccall, leaf)

    def printTopYangProps(self):
        for key in sorted(self.__yprops.keys()):
            if self.__yprops[key].getcontainer or self.__yprops[key].getaugmentstatus:
                yield "{}|{}|{}|{}".format(key,self.__yprops[key].getnamespace,self.__yprops[key].getprefix,self.__yprops[key].getcontainer)


    def printYangProps(self,ykey):
        print("Yang        |Namespace            |Prefix        | Container")
        if ykey in self.__yprops.keys():
            print ("%10s|%30s|%10s|%15s" %(ykey,self.__yprops[ykey].getnamespace,self.__yprops[ykey].getprefix,self.__yprops[ykey].getcontainer))
        else:
            print ("%s is unavailable" %ykey)

    def printAllYangProps(self):
        for key in sorted(self.__yprops.keys()):
            #if self.__yprops[key].getcontainer:
            yield "{}|{}|{}|{}".format(key,self.__yprops[key].getnamespace,self.__yprops[key].getprefix,self.__yprops[key].getcontainer)

    def downloadYang(self,destdir=None):
        reason="\n"
        fyang=""
        if destdir is None:
            destdir=self.__ypath
        if not os.path.isdir(destdir):
            os.mkdir(destdir)
        for c in self.__myyangs:
            try:
                data = self.__mydevice.get_schema(identifier=c)
                data = str(data).replace('encoding="UTF-8"', '')
                root = etree.fromstring(str(data))
                c=os.path.join(destdir, c)
                for log in root:
                    with open("%s.yang" %c, "wb") as f:
                        f.write(log.text.encode('utf-8'))
            except Exception as e:
                reason=reason+str(e)+"\n"
                fyang=fyang+c+"-"
        else:
            if fyang.__len__() > 1:
                return (-2,reason,fyang)
            else:
                return (0, reason,None)

    def doRPC(self,ykey,rpccall):
        self.__yprops[ykey].parseRPCYang()
        for name in self.printRPCNames(ykey):
            print ("RPC call 1: %30s" %name)
        rpccall = input("Ener RPC call: ")
        if self.__actiontag is None:
            return(-1,"No ACTION TAG DEFINED")
        CONTENT = "<action xmlns=\"" + self.__actiontag + "\">\n<data>\n"
        CONTENT = CONTENT + "<" + self.__yprops[ykey].getprefix + " xmlns=\"" + self.__yprops[ykey].getnamespace + "\">\n"
        CONTENT = CONTENT + "<" + rpccall + ">"
        
        print ("-----------------------Please provide values for below  attributes-----------------------------")
        for leaf in self.__yprops[ykey].returnLeafs(rpccall):
            tempdict=self.__yprops[ykey].returnLeafProps(rpccall,leaf)
            print ("%r" %tempdict)
            if tempdict['default']:
                if tempdict['mandatory']:
                    print ("########### THIS VALUE IS MANDATORY  ######################")
                stmt = "Enter value for {} - (Default: {})   : ".format(leaf,tempdict['default'])
                print ("Type -> %s\nDescription -> %s\n,Allowed values -> %s\n"%(tempdict['type'],tempdict['description'],tempdict['values']))
                user_in=input(stmt)
                user_in = user_in.strip()
                if user_in == "":
                    CONTENT = CONTENT + "\n<" + leaf + ">" + tempdict['default'] + "</" + leaf + ">"
                else:
                    CONTENT = CONTENT + "\n<" + leaf + ">" + user_in + "</" + leaf + ">"
            else:
                if tempdict['mandatory']:
                    print ("########### THIS VALUE IS MANDATORY  ######################")
                stmt="Enter value for {}   : ".format(leaf)
                print ("Type -> %s\nDescription -> %s\nDefault -> %s\nAllowed values -> %s\n"%(tempdict['type'],tempdict['description'],tempdict['default'],tempdict['values']))
                user_in=input(stmt)
                user_in = user_in.strip()
                if user_in != "skip" and user_in != "":
                    CONTENT = CONTENT + "\n<" + leaf + ">" + user_in + "</" + leaf + ">"

        CONTENT = CONTENT + "\n</" + rpccall + ">"
        CONTENT = CONTENT + "\n</" + self.__yprops[ykey].getprefix + ">" + "\n</data>\n</action>"
        print ("CONTENT is %s" %CONTENT)
        c = self.__mydevice.dispatch(to_ele(CONTENT)).data_xml
        print("%s" % c)
        
    def RPCdispatch(self,inputxml):
        print("RPC Call Initiated")
        output=self.__mydevice.dispatch(to_ele(inputxml)).data_xml
        print("RPC Call Completed")
        return output

    def setYangProps(self,ydir=None):
        reason=""
        count=0
        myang=""
        if ydir is None:
            ydir=self.__ypath
        if not os.path.isdir(ydir):
            reason = "{} does not exists, please check & try again".format(ydir)
            return (-1, reason)
        for c in self.__myyangs:
            c = os.path.join(ydir, c)
            if os.path.isfile(c+".yang"):
                self.__yprops[os.path.basename(c)]=YangParser(c+".yang")
                self.__prefixtonamespace[self.__yprops[os.path.basename(c)].getprefix]=self.__yprops[os.path.basename(c)].getnamespace
                count=count+1
        if count == 0:
            return(-2,"No yangs available in specified directory")
        YangParser.setGlobal(self.__prefixtonamespace)
        for c in self.__myyangs:
            try:
                if self.__yprops[c].getaugmentstatus:
                    self.__yprops[c].getContainerandLeaf()
            except KeyError as e:
                myang=myang+","+c
        if len(myang)>0:
            reason="Missing yang file for "+myang+" capability.\nEnsure yang folders has all yangs downloaded for proper processing."
            return(1,reason)
        return (0, reason)

    def simpleget(self,mode,outdir,filterstring):
        cout="ERROR"
        tstamp=int(time.time())
        outfile="Custom_"+mode+str(tstamp)
        if outdir:
            outfile=os.path.join(outdir,outfile)
        else:
            outfile = os.path.join(self.__ypath, outfile)
        try:
            print("Performing %s operation with - \n %s" % (mode, filterstring))
            if mode == 'Get':
                c = self.__mydevice.get(filter=filterstring).data_xml
                cout = c
            elif mode == 'Getconfig':
                c = self.__mydevice.get_config(source='running', filter=filterstring).data_xml
                cout = c
            if c.strip().endswith("</data>"):
                with open("%s.xml" %outfile, 'w') as f:
                    f.write(c)
                c = outfile
                status = 0
            else:
                c = "No data available"
                status = -1
        except Exception as e:
            c = str(e)
            status = -2
            print("RETURNING")
            return (status, c, cout)
        return (status, c, cout)

    def get(self,mode,ykey,ykey2=None,outdir=None,filterstring=None):
        #print("Called with args "+mode+" "+ykey+" "+ykey2+" "+outdir)
        if filterstring:
            (status,c,cout)=self.simpleget(mode,outdir,filterstring)
            return (status, c, cout)
        nspace2=None
        ykey2leaf=None
        cout="ERROR"
        outfile=mode+"_"+str(self.__deviceip)+"_"+str(ykey)
        if ykey2 and ykey2.find(":")>0:
            (ykey2id,ykey2leaf)=ykey2.split(":")
            #print("Ykey2id is "+ykey2id+" ykey2leaf is "+ykey2leaf)
        if outdir:
            outfile=os.path.join(outdir,outfile)
        else:
            outfile = os.path.join(self.__ypath, outfile)

        if ykey2 and ykey in self.__yprops.keys() and self.__yprops[ykey].getaugmentstatus:
            nspace = self.__yprops[ykey].getnamespace
            nspace2= str(self.__yprops[ykey].getaugnamespace(ykey2id))
            prefix = self.__yprops[ykey].getprefix
            prefix2 = self.__yprops[ykey].getaugprefix(ykey2id)
            containers = self.__yprops[ykey].getaugcontainers(ykey2id)
        elif ykey in self.__yprops.keys() and self.__yprops[ykey].getcontainer:
            nspace=self.__yprops[ykey].getnamespace
            prefix=self.__yprops[ykey].getprefix
            container=self.__yprops[ykey].getcontainer
            starttag = "<" + container + " "
            endtag = "</" + container + ">"
        else:
            print("RETURNING")
            return (-3, "No top level container found!!", None)
            
            '''if container is None:
                return (-2,"No top level container found",None)'''

        if nspace2:
            MyFilter = '''<filter>\n\t<{} xmlns:{}="{}" xmlns:{}="{}">'''.format(containers[0],prefix, nspace, prefix2, nspace2)
            for x in range(1,len(containers)):
                MyFilter=MyFilter+"\n<"+containers[x]+">"
            MyFilter=MyFilter+"\n<"+prefix+":"+ykey2leaf+"/>"
            for x in range(len(containers)-1,-1,-1):
                MyFilter=MyFilter+"\n</"+containers[x]+">"
            MyFilter=MyFilter+"\n</filter>"
        elif ykey2leaf:
            MyFilter = '''<filter>\n\t<{}:{} xmlns:{}="{}">'''.format(prefix, container, prefix, nspace)
            MyFilter = MyFilter+"\n"+"<"+prefix+":"+ykey2leaf+"/>"
            MyFilter = MyFilter+"\n</"+prefix+":"+container+">"
            MyFilter = MyFilter+"\n</filter>"
        else:
            MyFilter='''<filter>\n\t<{}:{} xmlns:{}="{}"/>\n</filter>'''.format(prefix,container,prefix,nspace)
        try:
            print("Performing %s operation with - \n %s" %(mode,MyFilter))
            if mode=='Get':
                c=self.__mydevice.get(filter=MyFilter).data_xml
                cout=c
            elif mode == 'Getconfig':
                c=self.__mydevice.get_config(source='running',filter=MyFilter).data_xml
                cout=c

            if nspace2 and c.strip().endswith("</data>"):
                with open("%s.xml" % outfile, 'w') as f:
                    f.write(c)
                c = outfile
                status = 0
            elif c.strip().endswith("</data>") and c.find(starttag) > 0 and c.find(endtag) > 0:
                with open("%s.xml" %outfile, 'w') as f:
                    f.write(c)
                c=outfile
                status=0
            else:
                c="No data available"
                status=-1
        except Exception as e:
            c=str(e)
            status=-2
            print("RETURNING")
            return(status,c,cout)
        return(status,c,cout)

if __name__=="__main__":
    print("Initialize your netconf device here.")
    #Device=Client(<IP_ADDRESS>,<USERNAME>,<PASSWORD>,<PORT_NUMBER>)
 
