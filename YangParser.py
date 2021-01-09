import re, os, argparse, logging, time, copy

class YangParser:
    prefixtoNS = {}

    def __init__(self,fname):
        self.__augment = False
        self.__yang=fname
        self.__namespace=None
        self.__prefix=None
        self.__container=None
        self.__usesmodules = []
        self.__rpcinput = {}
        self.__augobject = {}
        self.parseYang()


    @staticmethod
    def setGlobal(passeddict=None):
        YangParser.prefixtoNS = passeddict

    @property
    def getaugmentstatus(self):
        return self.__augment

    @property
    def parentdir(self):
        if os.path.dirname(self.__yang):
            return os.path.dirname(self.__yang)
        else:
            return os.getcwd()

    @property
    def yangname(self):
        return os.path.basename(self.__yang)

    @property
    def fullyangname(self):
        return self.__yang

    @property
    def getnamespace(self):
        return self.__namespace
    
    def getaugnamespace(self,ykey):
        return self.__augobject[ykey]["namespace"][0]

    def getaugcontainers(self,ykey):
        return self.__augobject[ykey]["containers"]

    def getaugleafs(self,ykey):
        return self.__augobject[ykey]["leafs"]

    def getaugprefix(self,ykey):
        return self.__augobject[ykey]["containers"][0].split(":")[0]

    @property
    def getprefix(self):
        return self.__prefix

    @property
    def getcontainer(self):
        return self.__container

    @property
    def getMainModules(self):
        for entry in self.__usesmodules:
            yield entry
        #return self.__usesmodules

    @property
    def ifRPCSupported(self):
        if len(self.__rpcinput) > 0:
            return True
        else:
            return False

    def printRPCs(self):
        for c in self.__rpcinput.keys():
            yield c

    def printUses(self):
        #retrun self.__usesmodules
        for c in self.__usesmodules:
            #print("Retruning " + c)
            yield c

    def returnUses(self):
        return self.__usesmodules

    def printAugs(self):
        #return self.__augobject
        for c in self.__augobject.keys():
            for c1 in self.__augobject[c]["leafs"]:
                yield c+":"+c1

    def returnAugs(self):
        return self.__augobject

    def printRPCValues(self):
        for key in self.__rpcinput.keys():
            print ("For %s call:" %key)
            for key1 in self.__rpcinput[key].keys():
                print ("Leaf is %s" %key1)
                for key2 in self.__rpcinput[key][key1].keys():
                    print ("%s is %s" %(key2,self.__rpcinput[key][key1][key2]))

    def returnLeafs(self,rpccall):
        for key in self.__rpcinput[rpccall].keys():
                yield key
    
    def returnLeafProps(self,rpccall,leaf):
         return self.__rpcinput[rpccall][leaf]
    
    def parseRPCYang(self):
        enc="utf-8"
        foundrpcb=foundr=foundl=founddesc=foundman=founddef=foundtype=0
        lline=descline=mandline=defline=typeline=" "
        actionitemre = re.compile("[\s]*tailf:action[\s]+([\S-]+?)[\s]*{")
        inputre = re.compile("[\s]+input[\s]*{")
        rpcitemre = re.compile("[\s]*rpc[\s]+([\S-]+?)[\s]*{")
        leafre = re.compile("[\s]+(leaf|choice|container|anyxml)[\s]+([\S]+?)[\s]*{")
        descre = re.compile("[\s]+description[\s]+[\"]{0,1}(.*)[\"]{0,1}[\s]*;")
        typere = re.compile("[\s]+type[\s]+([\S]+?)[\s]*;")
        mandre = re.compile("[\s]+mandatory[\s]+([\S]+?)[\s]*;")
        defaultre = re.compile("[\s]+default[\s]+[\"]{0,1}(.*)[\"]{0,1}[\s]*;")

        for line in open(self.__yang, encoding=enc):
            #print ("Processing line: %s for %s" %(line,self.yangname))
            #print("Top Foundl value is %d" %foundl)

            if actionitemre.search(line):
                CurRpc=actionitemre.search(line).group(1).replace("\"","")
                self.__rpcinput[CurRpc] = {}
            if rpcitemre.search(line):
                CurRpc=rpcitemre.search(line).group(1).replace("\"","")
                self.__rpcinput[CurRpc] = {}
            if foundl==1 or (leafre.search(line) and foundr==1):
                lline+=line
                foundl = 1
                if leafre.search(lline):
                    myleaf=leafre.search(lline).group(2).replace("\"","")
                    self.__rpcinput[CurRpc][myleaf]={}
                    for x in ["type", "description", "mandatory", "default","values"]:
                        self.__rpcinput[CurRpc][myleaf][x]=None
                    lline=""
                    foundl=0
            if founddef==1 or (line.find("default")>=0 and foundr==1):
                defline+=line
                founddef = 1
                if defaultre.search(defline):
                    self.__rpcinput[CurRpc][myleaf]['default']=defaultre.search(defline).group(1).replace("\"","")
                    defline=""
                    founddef=0
            if foundman==1 or (line.find("mandatory")>=0 and foundr==1):
                mandline+=line
                foundman = 1
                if mandre.search(mandline):
                    self.__rpcinput[CurRpc][myleaf]['mandatory']=mandre.search(mandline).group(1).replace("\"","")
                    mandline=""
                    foundman=0
            if foundtype==1 or (line.find("type")>=0 and foundr==1):
                typeline+=line
                foundtype = 1
                if typere.search(typeline):
                    self.__rpcinput[CurRpc][myleaf]['type']=typere.search(typeline).group(1).replace("\"","")
                    if self.__rpcinput[CurRpc][myleaf]['type'].find("boolean") >= 0:
                        self.__rpcinput[CurRpc][myleaf]['values']=["true","false"]
                    elif self.__rpcinput[CurRpc][myleaf]['type'].find(":") >= 0:
                        (basefile, LookForEnum) = self.__rpcinput[CurRpc][myleaf]['type'].split(":")
                        LookForEnum = LookForEnum.replace(";", "")
                        basefile=basefile+".yang"
                        basefile = os.path.join(self.parentdir, basefile)
                        if os.path.isfile(basefile):
                            content1 = ""
                            valuesenum = []
                            for line in open(basefile, encoding=enc):
                                content1 = content1 + "\n" + line

                            valuescond = "[\s]+typedef[\s]*" + LookForEnum + "[\s]*{([\S\s]*?)}[\s]*}[\s]*}"
                            valuesre = re.compile(valuescond)
                            if valuesre.search(content1):
                                valuesection = valuesre.search(content1).group(1).split("\n")
                                for line in valuesection:
                                    line = line.strip()
                                    if line.startswith("enum"):
                                        valuesenum.append(line.split(" ")[1].replace("\"",""))
                                self.__rpcinput[CurRpc][myleaf]['values'] = valuesenum
                    foundtype=0
                    typeline=""
            if founddesc==1 or (line.find("description")>=0 and foundr==1):
                temp=line.strip()
                descline=descline+" "+temp
                founddesc = 1
                if descre.search(descline):
                    self.__rpcinput[CurRpc][myleaf]['description']=descre.search(descline).group(1).replace("\"","")
                    #print ("Nithin: Desc  %s" %self.__rpcinput[CurRpc][myleaf]['description'])
                    descline=""
                    founddesc=0
            if inputre.search(line):
                foundr=1 #Entered input section
            if foundr == 1 and line.find("{") >= 0:
                foundrpcb+=line.count("{")
            if foundr == 1 and line.find("}") >= 0:
                foundrpcb-=line.count("}")
                if foundrpcb <= 0: #End of input section for a given RPC
                    foundr=0


    def parseYang(self):
        enc="utf-8"
        first=foundb=foundp=foundns=foundc=entersection=0
        cline=" "
        namespaceremultiline = re.compile("^[\s]+namespace[\s]*\"([\S]+?)\";")
        prefixre = re.compile("^[\s]+prefix[\s]*[\"]{0,1}([\S]+?)[\"]{0,1};")
        containerre = re.compile("[\s]*container[\s]+([\S]+?)[\s]*{")
        leafre = re.compile("[\s]+leaf[\s]+([\S]+?)[\s]*{")
        usesre = re.compile("[\s]+uses[\s]+([\S]+?)[\s]*;")

        for line in open(self.__yang,encoding=enc):
            if line.strip().startswith("augment") and self.__container is None:
                self.__augment = True
            if foundns == 0 and namespaceremultiline.search(line):
                self.__namespace=namespaceremultiline.search(line).group(1).replace("\"","")
                foundns=1
            if foundp == 0 and prefixre.search(line):
                self.__prefix=prefixre.search(line).group(1).replace("\"","")
                foundp=1
            if entersection == 1:
                if foundb == 1:
                    break
                if usesre.search(line) and foundb==2:
                    self.__usesmodules.append(usesre.search(line).group(1).replace("\"",""))
            if (foundc == 1 or line.strip().startswith("container")) and foundb == 1 and self.__container is None:
                cline+=line
                foundc=1
                if containerre.search(cline):
                    self.__container=containerre.search(cline).group(1).replace("\"","")
                    self.__augment=False
                    entersection=1
                    #break
            if first==0 and line.find("{") >= 0:
                foundb=line.count("{")
                first=1
            elif line.find("{") >= 0:
                foundb += line.count("{")
            if line.find("}") >= 0:
                foundb -= line.count("}")
            prevline=line

    def getContainerandLeaf(self):
        #print("Called")
        enc="utf-8"
        breakcond=100
        augprefix=[]
        augcontainer=[]
        augnamespace=[]
        augleaf=[]
        foundb=entersection=0
        augmentre = re.compile("[\s]+augment[\s]+([\S:/]+?)[\s]*{")
        usesre = re.compile("[\s]+uses[\s]+([\S]+?)[\s]*;")
        leafre = re.compile("[\s]+leaf[\s]+([\S]+?)[\s]*{")
        leaflistre = re.compile("[\s]+leaf-list[\s]+([\S]+?)[\s]*{")
        containerre = re.compile("[\s]+container[\s]+([\S]+?)[\s]*{")

        for line in open(self.__yang,encoding=enc):
            if line.find("{") >= 0:
                foundb += line.count("{")
            if line.find("}") >= 0:
                foundb -= line.count("}")
            if breakcond==foundb:
                if value not in self.__augobject.keys():
                    #print("Updating values under breakcond "+value)
                    #print("Namesapce is %r \n container is %r \n leafs is %r \n" %(augnamespace,augcontainer,augleaf))

                    self.__augobject[value]={}
                    self.__augobject[value]["namespace"]=copy.deepcopy(augnamespace)
                    self.__augobject[value]["containers"]=copy.deepcopy(augcontainer)
                    if not self.__container:
                        self.__augobject[value]["leafs"]=copy.deepcopy(augleaf)
                    else:
                        self.__augobject[value]["leafs"]=copy.deepcopy(self.__container)
                    #print("Object is %r" %self.__augobject)
                    #tempx = input("ENTER")
                augnamespace.clear()
                augcontainer.clear()
                augleaf.clear()
                entersection=0
            #print("Reading line "+line)
            #print("OBject is %r" % self.__augobject)

            if entersection==0 and augmentre.search(line):
                #print("MATCHED "+line)
                breakcond=foundb-1
                entersection=1
                augsection=augmentre.search(line).group(1).replace("\"","")
                for entry in augsection.split("/"):
                    #print("Entry is " + entry)
                    if entry == "":
                        #print("skip")
                        continue
                    temp=entry.split(":")[0]
                    #print("Temp is " + temp)
                    #print("Prefix is %r" %augprefix)
                    augprefix.append(temp)
                    #print("Prefix is %r" %augprefix)
                    augcontainer.append(entry)
                    #print("Prefix is %r" %augprefix)
                value=entry.split(":")[1]
                #print("Prefix is %r" %augprefix)
                for x in set(augprefix):
                        augnamespace.append(YangParser.prefixtoNS[x])
                        #print("For %s \n Namesapce is %r" %(x,augnamespace))
                        #tempx=input("ENTER")
                augprefix.clear()
            if entersection == 1:
                if leafre.search(line):
                    augleaf.append(leafre.search(line).group(1).replace("\"",""))
                if leaflistre.search(line):
                    augleaf.append(leaflistre.search(line).group(1).replace("\"",""))
                if containerre.search(line):
                    augleaf.clear()
                    #("Updating values under container if cond "+value)
                    #print("Namesapce is %r \n container is %r \n leafs is %r \n" %(augnamespace,augcontainer,augleaf))
                    self.__container=containerre.search(line).group(1).replace("\"","")
                    augleaf.append(self.__container)
                    self.__augobject[value] = {}
                    self.__augobject[value]["namespace"] = copy.deepcopy(augnamespace)
                    self.__augobject[value]["containers"] = copy.deepcopy(augcontainer)
                    self.__augobject[value]["leafs"]=copy.deepcopy(augleaf)
                    augnamespace.clear()
                    augcontainer.clear()
                    augleaf.clear()
                    entersection = 0
                    #print("Object is %r" %self.__augobject)
                    #tempx = input("ENTER")
                if usesre.search(line):
                    (temp,type)=self.getleafs(usesre.search(line).group(1).replace("\"",""))
                    if type==2:
                        #print("Updating values under type 2 if cond " + value)
                        #print("Namesapce is %r \n container is %r \n leafs is %r \n" % (augnamespace, augcontainer, temp))
                        augleaf.clear()
                        self.__container=temp
                        self.__augobject[value]={}
                        self.__augobject[value]["namespace"] = copy.deepcopy(augnamespace)
                        self.__augobject[value]["containers"] = copy.deepcopy(augcontainer)
                        augleaf.append(temp)
                        self.__augobject[value]["leafs"]=copy.deepcopy(augleaf)
                        #print("OBject is %r" %self.__augobject)
                        #tempx=input("ENTER")
                        augleaf.clear()
                        augnamespace.clear()
                        augcontainer.clear()
                        entersection = 0
                    else:
                        for x in temp:
                            augleaf.append(x)
        '''for c in self.printAugs():
            print ("Augs is "+c)
        print("%r" %self.__augobject)'''


    def getleafs(self,gstring):
        enc="utf-8"
        breakcond=100
        foundb=groupsection=0
        tempaugleaf=[]
        gregexstr='[\s]+grouping[\s]+[\"]{{0,1}}{}[\"]{{0,1}}[\s]*{{'.format(gstring)
        groupingre=re.compile(gregexstr)
        leafre = re.compile("[\s]+leaf[\s]+([\S]+?)[\s]*{")
        leaflistre = re.compile("[\s]+leaf-list[\s]+([\S]+?)[\s]*{")
        containerre = re.compile("[\s]+container[\s]+([\S]+?)[\s]*{")
        #print("TRYING TO MATCTH FOR %r" %gregexstr)
        for line in open(self.__yang,encoding=enc):
            if groupsection==0 and groupingre.search(line):
                groupsection=1
                breakcond=foundb
            if groupsection==1:
                if leafre.search(line):
                    tempaugleaf.append(leafre.search(line).group(1).replace("\"", ""))
                if leaflistre.search(line):
                    tempaugleaf.append(leaflistre.search(line).group(1).replace("\"", ""))
                if containerre.search(line):
                    #print("Returning %r - 2"%containerre.search(line).group(1).replace("\"", ""))
                    return (containerre.search(line).group(1).replace("\"", ""),2)
            if line.find("{") >= 0:
                    foundb += line.count("{")
            if line.find("}") >= 0:
                foundb -= line.count("}")
            if breakcond==foundb:
                #print("Returning %r - 1"%tempaugleaf)
                return (tempaugleaf,1)
        #print("NO MATCTH FOR %r" %gregexstr)


if __name__ == "__main__":
    print("Initialize your YangParser Object here.")
    #nyang=YangParser(<ABSOLUTE_PATH_FOR_YANG_FILE>)
    