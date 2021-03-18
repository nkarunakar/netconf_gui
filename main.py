import sys,time,os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QMessageBox, QLineEdit, QComboBox, QFileDialog, QCheckBox, QTextEdit
import Client
from PyQt5 import QtCore, QtGui
from lxml import etree
from PyQt5.QtCore import QRunnable, QThreadPool,QObject,pyqtSignal
from PyQt5.QtGui import QMovie,QPixmap


class NCMenu(QWidget):
    def __init__(self, parent=None):
        super(NCMenu, self).__init__(parent)
        self.w=QWidget()
        self.w.resize(500,500)
        self.w.setWindowTitle('NCCLient')
        self.threadpool = QThreadPool()
        self.customfilter=None

        self.blockerUI = QMessageBox(self.w)
        self.blockerUI.setStandardButtons(QMessageBox.NoButton)
        self.imagepath1=os.path.join("images","Loading_Key.ico")
        self.blockerUI.setIconPixmap(QPixmap(self.imagepath1).scaledToWidth(100))
        self.icon_label = self.blockerUI.findChild(QLabel, "qt_msgboxex_icon_label")
        self.movie = QMovie(self.imagepath1)
        # avoid garbage collector
        setattr(self.blockerUI, 'icon_label', self.movie)
        self.icon_label.setMovie(self.movie)
        self.movie.start()
        self.blockerUI.setText("Please wait...")
        self.blockerUI.setWindowTitle("Processing request")
        self.blockerUI.setModal(False)

        self.savedbuttons={}
        self.inputbuttons=[]
        self.checkboxarray=[]
        self.lineditarray=[]
        self.comboarray=[]
        self.retstatus=None
        self.retmessage=None
        self.retmessage1=None
        self.connect=0

        self.mainlabelFont = QtGui.QFont("Calibri",15,75)
        childlabelFont = QtGui.QFont("Calibri", 15, 75)

        self.mainlabel = QLabel(self.w)
        self.mainlabel.setFont(self.mainlabelFont)
        self.mainlabel.setText("Enter the device details")
        self.mainlabel.move(80, 30)
        self.mainlabel.show()

        self.iplabel = QLabel(self.w)
        self.iplabel.setText("IP address:")
        self.iplabel.move(80, 80)
        self.iplabel.show()
        self.ip_lineedit = QLineEdit(self.w)
        self.ip_lineedit.setText('<IP_ADDRESS>')
        self.ip_lineedit.move(140, 80)

        self.usernamelabel = QLabel(self.w)
        self.usernamelabel.setText("Username:")
        self.usernamelabel.move(80, 110)
        self.usernamelabel.show()
        self.username_lineedit = QLineEdit(self.w)
        self.username_lineedit.setText('<USERNAME>')
        self.username_lineedit.move(140, 110)

        self.passwordlabel = QLabel(self.w)
        self.passwordlabel.setText("Password:")
        self.passwordlabel.move(80, 140)
        self.passwordlabel.show()
        self.password_lineedit = QLineEdit(self.w)
        self.password_lineedit.setEchoMode(2)
        self.password_lineedit.setText('<PASSWORD>')
        self.password_lineedit.move(140, 140)

        self.portlabel = QLabel(self.w)
        self.portlabel.setText("Port:")
        self.portlabel.move(80, 170)
        self.portlabel.show()
        self.port_lineedit = QLineEdit(self.w)
        self.port_lineedit.setText('830')
        self.port_lineedit.move(140, 170)

        #self.ip_lineedit.returnPressed.connect(self.dialog)
        self.devconnect = QPushButton(self.w)
        self.devconnect.setText('CONNECT')
        self.devconnect.setGeometry(140,210,200,22)
        self.devconnect.clicked.connect(self.postConnect)

        self.lyangbtn = QPushButton(self.w)
        self.lyangbtn.setText('LOAD YANGS')
        self.lyangbtn.setGeometry(140,240,200,22)
        self.lyangbtn.setEnabled(False)
        self.lyangbtn.clicked.connect(self.doLyang)

        self.ldirlabel = QLabel(self.w)
        self.ldirlabel.setText("Destination directory:")
        self.ldirlabel.move(30, 270)
        self.ldirlabel.show()
        self.ldir_lineedit = QLineEdit(self.w)
        self.ldir_lineedit.setText('None')
        self.ldir_lineedit.setEnabled(False)
        self.ldir_lineedit.move(140, 270)
        self.ldircbox=QCheckBox(self.w)
        self.ldircbox.setText("Use Default Path")
        self.ldircbox.move(140,290)
        self.ldircbox.setChecked(True)
        self.ldircbox.setEnabled(False)
        self.ldircbox.stateChanged.connect(self.toggleLdir)
        self.ldirbtn = QPushButton(self.w)
        self.ldirbtn.setText('BROWSE')
        #self.ldirbtn.size()
        self.ldirbtn.move(300, 270)
        self.ldirbtn.setEnabled(False)
        self.ldirbtn.clicked.connect(self.getDir)

        self.doopbtn = QPushButton(self.w)
        self.doopbtn.setText('DO OPERATIONS')
        self.doopbtn.setGeometry(140,320,200,22)
        self.doopbtn.setEnabled(False)
        self.doopbtn.clicked.connect(self.doOperations)

        self.dooplabel = QLabel(self.w)
        self.dooplabel.setText("Yang directory:")
        self.dooplabel.move(30, 350)
        self.dooplabel.show()
        self.doop_lineedit = QLineEdit(self.w)
        self.doop_lineedit.setText('None')
        self.doop_lineedit.setEnabled(False)
        self.doop_lineedit.move(140, 350)
        self.doopcbox=QCheckBox(self.w)
        self.doopcbox.setText("Use Default Path")
        self.doopcbox.move(140,370)
        self.doopcbox.setChecked(True)
        self.doopcbox.setEnabled(False)
        self.doopcbox.stateChanged.connect(self.toggleDoopDir)
        self.ddirbtn = QPushButton(self.w)
        self.ddirbtn.setText('BROWSE')
        #self.ldirbtn.size()
        self.ddirbtn.move(300, 350)
        self.ddirbtn.setEnabled(False)
        self.ddirbtn.clicked.connect(self.getDoopDir)

        self.aboutbtn = QPushButton(self.w)
        self.aboutbtn.setText('ABOUT')
        self.aboutbtn.setGeometry(140,400,200,22)
        self.aboutbtn.clicked.connect(self.about)

        self.closebtn = QPushButton(self.w)
        self.closebtn.setText('QUIT')
        self.closebtn.setGeometry(140,430,200,22)
        #Better to use sys.exit for more control on exit, maybe Do you really want to quit dialog box?
        self.closebtn.clicked.connect(self.closeandexit)
        #QtCore.QCoreApplication.instance().quit

        self.w.show()
        sys.exit(app.exec_())
        #TEMP=W
    def closeandexit(self):
        if self.connect==1:
            try:
                print("Closing connection")
                self.Device.disconnect()
            except Exception as e:
                repr(e)
                print (e)
        print("Exiting!")
        QtCore.QCoreApplication.instance().quit
        raise SystemExit

    def postConnect(self):
        flag=0
        try:
            self.Device = Client.Client(self.ip_lineedit.text(),self.username_lineedit.text(),self.password_lineedit.text(),self.port_lineedit.text())
            self.connect=1
        except Exception as e:
            mbox = QMessageBox(self.w)
            mbox.setWindowTitle("ERROR MESSAGE")
            mbox.setIcon(QMessageBox.Warning)
            mbox.setText("Error encountered on connect operation")
            mbox.setDetailedText(str(e))
            mbox.setStandardButtons(QMessageBox.Ok)
            mbox.exec_()
            flag=1
        if flag==0:
            self.devconnect.setEnabled(False)
            self.devconnect.setText('CONNECTED')
            self.dir =  self.Device.getDefaultYPath
            self.ddir = self.Device.getDefaultYPath
            self.ldir_lineedit.setText(self.dir)
            self.doop_lineedit.setText(self.ddir)
            self.lyangbtn.setEnabled(True)
            self.ldir_lineedit.setEnabled(True)
            self.ldircbox.setEnabled(True)

            self.doopbtn.setEnabled(True)
            self.doop_lineedit.setEnabled(True)
            self.doopcbox.setEnabled(True)

    def doLyang(self):
        self.lyangbtn.setText("Downloading Yangs")
        worker = Worker(self.Device.downloadYang,self.dir)
        self.threadpool.start(worker)
        self.w.setEnabled(False)
        blockmsg="Please check "+self.dir+" to check status of download"
        self.blockerUI.setText(blockmsg)
        self.blockerUI.show()
        worker.signals.finished.connect(self.closeMyLoop)
        worker.signals.result.connect(self.goAheadwithDL)

    def closeMyLoop(self):
        self.w.setEnabled(True)
        self.blockerUI.done(1)

    def closeMyGLoop(self):
        self.w1.setEnabled(True)
        self.blockerUI1.done(1)

    def goAheadwithDL(self,status,message=None,message1=None):
        self.retstatus = status
        self.retmessage = message
        self.retmessage1 = message1
        if self.retstatus:
            #print("%s %s" % (status, out))
            mbox = QMessageBox(self.w)
            errmsg="ERROR MESSAGE: Please check "+self.dir+" directory for yangs"
            mbox.setWindowTitle(errmsg)
            mbox.setIcon(QMessageBox.Warning)
            mbox.setText(self.retmessage)
            failyang="Failed for: "+self.retmessage1
            mbox.setDetailedText(failyang)
            mbox.setStandardButtons(QMessageBox.Ok)
            mbox.exec_()
        else:
            mbox = QMessageBox(self.w)
            mbox.setWindowTitle("NC MESSAGE")
            mbox.setIcon(QMessageBox.Information)
            mbox.setText("All yangs downloaded successfully")
            failyang="Yangs are available in: "+self.dir
            mbox.setDetailedText(failyang)
            mbox.setStandardButtons(QMessageBox.Ok)
            mbox.exec_()
        self.lyangbtn.setText("DOWNLOADED YANGS")
        self.lyangbtn.setEnabled(False)
        self.ldirbtn.setEnabled(False)
        self.ldircbox.setEnabled(False)
        self.doopbtn.setEnabled(True)

    def doOperations(self):
        worker = Worker(self.Device.setYangProps,self.ddir)
        self.threadpool.start(worker)
        self.w.setEnabled(False)
        blockmsg="Please wait, processing yangs under "+self.ddir
        self.blockerUI.setText(blockmsg)
        self.blockerUI.show()
        worker.signals.finished.connect(self.closeMyLoop)
        worker.signals.result.connect(self.goAheadWithDoop)
    
    def goAheadWithDoop(self,status,message=None,message1=None):
        self.retstatus = status
        self.retmessage = message
        self.retmessage1 = message1
        if self.retstatus < 0:
            mbox = QMessageBox(self.w)
            mbox.setWindowTitle("ERROR MESSAGE")
            mbox.setIcon(QMessageBox.Warning)
            errmsg="Error encountered, please ensure yangs are available in "+self.ddir
            mbox.setText(errmsg)
            mbox.setDetailedText(self.retmessage)
            mbox.setStandardButtons(QMessageBox.Ok)
            mbox.exec_()
            #QtCore.QCoreApplication.instance().quit
        #self.Device = Client.Client(self.ip_lineedit.text(),self.username_lineedit.text(),self.password_lineedit.text(),self.port_lineedit.text())
        #self.w.close()
        else:
            if len(self.retmessage) > 0:
                mbox = QMessageBox(self.w)
                mbox.setWindowTitle("INFO MESSAGE")
                mbox.setIcon(QMessageBox.Warning)
                errmsg="Some yangs are unavailable in "+self.ddir+" Please check details"
                mbox.setText(errmsg)
                mbox.setDetailedText(self.retmessage)
                mbox.setStandardButtons(QMessageBox.Ok)
                mbox.exec_()
            self.doopbtn.setEnabled(False)
            self.ddirbtn.setEnabled(False)
            self.doopcbox.setEnabled(False)

            self.w1=QWidget()
            self.w1.resize(1100,820)
            self.w1.setWindowTitle('YangDetails')
            self.yanglabel = QLabel(self.w1)
            self.yanglabel.setText("Top Level Yangs with data")
            self.yanglabel.setFont(self.mainlabelFont)
            self.yanglabel.move(60, 40)
            self.yanglabel.show()
            self.yangcombobox=QComboBox(self.w1)
            self.yangcombobox.move(100,80)
            self.yangcombobox.currentTextChanged.connect(self.populatecbox2)
            self.yangcombobox1=QComboBox(self.w1)
            self.yangcombobox1.move(100,120)
            self.yangcombobox1.setEnabled(False)
            self.yangcombobox1.currentTextChanged.connect(self.populatecbox2)
            self.yangcombobox2=QComboBox(self.w1)
            self.yangcombobox2.resize(200, 25)
            self.yangcombobox2.move(100,160)
            self.yangcombobox2.setEnabled(False)

            self.blockerUI1 = QMessageBox(self.w1)
            self.blockerUI1.setStandardButtons(QMessageBox.NoButton)
            self.imagepath2=os.path.join("images","Loading_Key2.ico")
            self.blockerUI1.setIconPixmap(QPixmap(self.imagepath2).scaledToWidth(100))
            self.icon_label1 = self.blockerUI1.findChild(QLabel, "qt_msgboxex_icon_label")
            self.movie1 = QMovie(self.imagepath2)
        # avoid garbage collector
            setattr(self.blockerUI1, 'icon_label', self.movie1)
            self.icon_label1.setMovie(self.movie1)
            self.movie1.start()
            self.blockerUI1.setText("Please wait...")
            self.blockerUI1.setWindowTitle("Processing request")
            self.blockerUI1.setModal(False)

            self.yangcbox=QCheckBox(self.w1)
            self.yangcbox.setText("Use filtered yangs for get/getconfig")
            self.yangcbox.move(100,190)
            self.yangcbox.setChecked(False)
            self.yangcbox.setEnabled(True)
            self.yangcbox.stateChanged.connect(self.toggleyangCbox)

            self.textboxlabel1 = QLabel(self.w1)
            self.textboxlabel1.setText("Output:")
            self.textboxlabel1.move(450, 80)
            self.textboxlabel1.show()
            self.textbox1 = QTextEdit(self.w1)
            self.textbox1.move(450, 100)
            self.textbox1.resize(600, 700)
            self.textbox1.setReadOnly(True)

            for c in self.Device.printAllYangProps():
                y=c.split("|")[0]
                self.yangcombobox.addItem(y)

            for c in self.Device.printTopYangProps():
                y=c.split("|")[0]
                self.yangcombobox1.addItem(y)

            self.getb = QPushButton(self.w1)
            self.getb.setText('GET')
            self.getb.move(100, 230)
            self.getb.clicked.connect(self.get)

            self.gconfig = QPushButton(self.w1)
            self.gconfig.setText('GETCONFIG')
            self.gconfig.move(100, 270)
            self.gconfig.clicked.connect(self.getc)
            temp=self.yangcombobox.currentText()
            print("Selected %s" %temp)
        
            self.rpcbutton = QPushButton(self.w1)
            self.rpcbutton.setText('ACTION(TAILF)')
            self.rpcbutton.move(100, 310)
            if self.Device.getMyAtag is None:
                self.rpcbutton.setEnabled(False)
            self.rpcbutton.clicked.connect(self.rpcsection)

            self.clearsceen = QPushButton(self.w1)
            self.clearsceen.setText('CLEAR SCREEN')
            self.clearsceen.move(100, 350)
            self.clearsceen.clicked.connect(self.clearW1TBox)

            self.custom = QPushButton(self.w1)
            self.custom.setText('CUSTOM GET/GETCONFIG')
            self.custom.move(100, 390)
            self.custom.clicked.connect(self.getFilterString)

            self.closebtn1 = QPushButton(self.w1)
            self.closebtn1.setText('CLOSE')
            self.closebtn1.move(100, 430)
            self.closebtn1.clicked.connect(self.closeW1)

            self.w1.show()

    def getFilterString(self):
        self.w4 = QWidget()
        self.w4.resize(600,600)
        self.w4.setWindowTitle('ENTER CUSTOM XML')

        self.customget = QPushButton(self.w4)
        self.customget.setText('DO GET')
        self.customget.setGeometry(450,60,100,50)
        self.customget.setObjectName("CUSTOM")
        #self.customget.move(450, 60)
        self.customget.clicked.connect(self.get)

        self.customgetc = QPushButton(self.w4)
        self.customgetc.setText('DO GETCONFIG')
        self.customgetc.setObjectName("CUSTOM")
        self.customgetc.setGeometry(450,180,100,50)
        self.customgetc.clicked.connect(self.getc)

        self.customclose = QPushButton(self.w4)
        self.customclose.setText('CLOSE')
        self.customclose.setGeometry(450,300,100,50)
        self.customclose.clicked.connect(self.closeW4)

        self.xmlbox = QTextEdit(self.w4)
        self.xmlbox.move(40,40)
        self.xmlbox.resize(400, 500)
        self.xmlbox.setReadOnly(False)
        sampletext='''<filter>

// ADD PREFIX, NAMESPACES, LEAF NODES OR FILTER CRITERIA HERE //

</filter>'''
        self.xmlbox.setText(sampletext)
        self.w4.show()

    def closeW4(self):
        print("CLEARING")
        self.customfilter = None
        self.w4.close()


    def clearW1TBox(self):
        blank=""
        self.textbox1.setText(blank)

    def closeW1(self):
        self.w1.close()

    def rpcsection(self):
        self.w2 = QWidget()
        self.w2.resize(400, 700)
        self.w2.setWindowTitle('ACTION Details')
        if self.yangcbox.isChecked():
            self.rpcyang = self.yangcombobox1.currentText()
        else:
            self.rpcyang=self.yangcombobox.currentText()
        self.Device.parseyangforRPCs(self.rpcyang)
        self.rpclabel = QLabel(self.w2)
        self.rpclabel.setText("ACTION Calls list")
        self.rpclabel.setFont(self.mainlabelFont)
        self.rpclabel.move(60, 40)
        self.rpclabel.show()
        buttons=[]
        startx=80
        starty=80
        for (i,rpccall) in enumerate(self.Device.printRPCNames(self.rpcyang)):
            buttons.append(QPushButton(self.w2))
            buttons[i].move(80,starty)
            buttons[i].setText(rpccall)
            buttons[i].clicked.connect(self.getRPCCall)
            starty += 40
        self.w2.show()

    def getRPCCall(self):
        self.savedbuttons={}
        self.inputbuttons=[]
        self.checkboxarray=[]
        self.lineditarray=[]
        self.comboarray=[]
        temprpc = self.sender()
        self.selectedrpccall=temprpc.text()
        self.w3 = QWidget()
        self.w3.resize(1200, 1200)
        title="TAILF Actions - "+self.selectedrpccall
        self.w3.setWindowTitle(title)
        self.rpcalabel = QLabel(self.w3)
        self.rpcalabel.setText("Provide input")
        self.rpcalabel.setFont(self.mainlabelFont)
        self.rpcalabel.move(60, 40)
        self.rpcalabel.show()
        self.textboxlabel = QLabel(self.w3)
        self.textboxlabel.setText("Output:")
        self.textboxlabel.move(700, 80)
        self.textboxlabel.show()
        self.textbox = QTextEdit(self.w3)
        self.textbox.move(720, 100)
        self.textbox.resize(420, 700)
        self.textbox.setReadOnly(True)
        startx=80
        starty=80
        startlx=180
        startdx=80
        startly=80
        startdy=100
        labelarray=[]
        desclabelarray=[]
        j=k=l=0
        for i,leaf in enumerate(self.Device.printLeafsforRPC(self.rpcyang,self.selectedrpccall)):
            labelarray.append(QLabel(self.w3))
            labelarray[i].setText(leaf)
            labelarray[i].move(startx,starty)
            labelarray[i].show()
            starty=starty+80
            
            tempdict=self.Device.getLeafPropsforRPC(self.rpcyang,self.selectedrpccall,leaf)

            if tempdict['values']:
                self.comboarray.append(QComboBox(self.w3))
                self.comboarray[j].move(startlx,startly)
                for entry in tempdict['values']:
                    self.comboarray[j].addItem(entry)
                self.saveinputbuttons(leaf,self.comboarray[j])
                startly+=80
                j+=1
                if tempdict['mandatory'] is None:
                    self.checkboxarray.append(QCheckBox(self.w3))
                    self.checkboxarray[l].move(startlx+150,startly-80)
                    self.checkboxarray[l].setChecked(True)
                    self.checkboxarray[l].setText("Not mandatory")
                    self.checkboxarray[l].stateChanged.connect(self.toggleInput)
                    self.comboarray[j-1].setEnabled(False)
                    self.savebutton(self.checkboxarray[l],self.comboarray[j-1])
                    l+=1
            else:
                self.lineditarray.append(QLineEdit(self.w3))
                self.lineditarray[k].move(startlx,startly)
                self.lineditarray[k].setText(tempdict['default'])
                self.lineditarray[k].setToolTip(tempdict['type'])
                self.saveinputbuttons(leaf,self.lineditarray[k])
                k+=1
                startly += 80
                if tempdict['mandatory'] is None:
                    self.checkboxarray.append(QCheckBox(self.w3))
                    self.checkboxarray[l].move(startlx+150, startly-80)
                    self.checkboxarray[l].setChecked(True)
                    self.checkboxarray[l].setText("Not mandatory")
                    self.checkboxarray[l].stateChanged.connect(self.toggleInput)
                    self.lineditarray[k-1].setEnabled(False)
                    self.savebutton(self.checkboxarray[l],self.lineditarray[k-1])
                    l+=1

            desclabelarray.append(QLabel(self.w3))
            desclabelarray[i].move(startdx,startdy)
            if tempdict['description']:
                if len(tempdict['description']) > 110:
                    myDescription="DESCRIPTION: "+tempdict['description'][0:110]+"\n"+tempdict['description'][110:220]+"\n"+tempdict['description'][220:330]
                else:
                    myDescription="DESCRIPTION: "+tempdict['description']
            else:
                myDescription="DESCRIPTION: Not Available"
            desclabelarray[i].setText(myDescription)
            startdy+=80
            desclabelarray[i].show()

        self.sendrpcclearcmd = QPushButton(self.w3)
        self.sendrpcclearcmd.setText('CLEAR OUTPUT SCREEN')
        self.sendrpcclearcmd.setFont(self.mainlabelFont)
        self.sendrpcclearcmd.move(startdx,startdy+20)
        self.sendrpcclearcmd.clicked.connect(self.clearW3Tbox)

        self.sendrpccmd = QPushButton(self.w3)
        self.sendrpccmd.setText('SEND')
        self.sendrpccmd.setFont(self.mainlabelFont)
        self.sendrpccmd.setGeometry(startdx,startdy+60,300,50)
        self.sendrpccmd.clicked.connect(self.executeRPC)

        self.viewrpcout = QLineEdit(self.w3)
        self.viewrpcout.setGeometry(80,900,200,900)
        self.viewrpcout.setText('TAILF/ACTION OUTPUT SEEN HERE')
        self.w3.show()

    def clearW3Tbox(self):
        blank=""
        self.textbox.setText(blank)

    def savebutton(self,sourcecbox,targetinput):
        self.savedbuttons[sourcecbox]=targetinput

    def saveinputbuttons(self,leaf,assocobj):
        self.inputbuttons.append((leaf,assocobj))

    def executeRPC(self):
        startblock=self.Device.returnRPCOpenBlock(ykey=self.rpcyang)
        endblock=self.Device.returnRPCCloseBlock(ykey=self.rpcyang)
        openrpcblock="\n<" + self.selectedrpccall + ">"
        closerpcblock="\n</" + self.selectedrpccall + ">"
        middleblock=""
        for (leaf,inputobj) in self.inputbuttons:
            leafValue=None
            if isinstance(inputobj,QLineEdit):
                if inputobj.isEnabled():
                    leafValue=inputobj.text()
            if isinstance(inputobj,QComboBox):
                if inputobj.isEnabled():
                    leafValue=inputobj.currentText()
            if leafValue:
                middleblock+="\n<"+leaf+">"+leafValue+"</"+leaf+">"
        finalrpcxml=startblock+openrpcblock+middleblock+closerpcblock+endblock
        try:
            c = self.Device.RPCdispatch(finalrpcxml)
            self.textbox.setText(c)
        except Exception as e:
            mbox = QMessageBox(self.w3)
            mbox.setWindowTitle("ERROR MESSAGE")
            mbox.setIcon(QMessageBox.Warning)
            mbox.setText("Error encountered on RPC operation")
            mbox.setDetailedText(str(e))
            mbox.setStandardButtons(QMessageBox.Ok)
            mbox.exec_()
        try:
            root = etree.fromstring(bytes(c,encoding='utf-8'))
            self.textbox.setText(etree.tostring(root, pretty_print=True).decode())
        except Exception as e:
            mboxe = QMessageBox(self.w3)
            mboxe.setWindowTitle("ERROR MESSAGE")
            mboxe.setIcon(QMessageBox.Warning)
            mboxe.setText("Unable to pretty print XML output")
            mboxe.setDetailedText(str(e))
            mboxe.setStandardButtons(QMessageBox.Ok)
            mboxe.exec_()
            #textboxlabel = QLabel(self.w3)


    def get(self):
        sourceobj=self.sender()
        if sourceobj.objectName() == "CUSTOM":
            self.customfilter = self.xmlbox.toPlainText()
        else:
            self.customfilter = None
        if self.yangcbox.isChecked():
            if self.yangcombobox2.currentText() is None:
                #print("Calling get with " + self.yangcombobox1.currentText())
                worker = GWorker(self.Device.get, mode="Get", ykey=self.yangcombobox1.currentText(),ykey2=None,outdir=self.ddir,filterstring=self.customfilter)
            else:
                #print("Calling get with " + self.yangcombobox1.currentText() + " and " + self.yangcombobox2.currentText() )
                worker = GWorker(self.Device.get, mode="Get", ykey=self.yangcombobox1.currentText(),ykey2=self.yangcombobox2.currentText(),outdir=self.ddir,filterstring=self.customfilter)
            self.threadpool.start(worker)
            self.w1.setEnabled(False)
            blockmsg = "Please wait, processing GET request"
            self.blockerUI1.setText(blockmsg)
            self.blockerUI1.show()
            worker.signals.finished.connect(self.closeMyGLoop)
            worker.signals.result.connect(self.goAheadWithGet)
            #(status, out, callout) = self.Device.get(mode="Get", ykey=self.yangcombobox1.currentText(),outdir=self.ddir)
        else:
            #print("Calling get with " + self.yangcombobox.currentText())
            worker = GWorker(self.Device.get, mode="Get", ykey=self.yangcombobox.currentText(),ykey2=None, outdir=self.ddir,filterstring=self.customfilter)
            self.threadpool.start(worker)
            self.w1.setEnabled(False)
            blockmsg = "Please wait, processing GET request"
            self.blockerUI1.setText(blockmsg)
            self.blockerUI1.show()
            worker.signals.finished.connect(self.closeMyGLoop)
            worker.signals.result.connect(self.goAheadWithGet)
            #(status, out, callout) = self.Device.get(mode="Get",ykey=self.yangcombobox.currentText(), outdir=self.ddir)

    def goAheadWithGet(self,status,message=None,message1=None):
        self.customfilter = None
        self.retstatus = status
        self.retmessage = message
        self.retmessage1 = message1
        flag=0
        if self.retstatus:
            mbox = QMessageBox(self.w1)
            mbox.setWindowTitle("ERROR MESSAGE")
            mbox.setIcon(QMessageBox.Warning)
            mbox.setText("Error encountered on get operation")
            mbox.setDetailedText(self.retmessage)
            mbox.setStandardButtons(QMessageBox.Ok)
            mbox.exec_()
        else:
            mbox = QMessageBox(self.w1)
            mbox.setWindowTitle("NC MESSAGE")
            mbox.setIcon(QMessageBox.Information)
            mbox.setText("Output available click on details for filename")
            self.retmessage = self.retmessage + ".xml"
            try:
                root = etree.fromstring(bytes(self.retmessage1,encoding='utf-8'))
                self.textbox1.setText(etree.tostring(root, pretty_print=True).decode())
            except Exception as e:
                mboxe = QMessageBox(self.w1)
                mboxe.setWindowTitle("MESSAGE")
                mboxe.setIcon(QMessageBox.Warning)
                mboxe.setText("Unable to pretty print XML output")
                mboxe.setDetailedText(str(e))
                mboxe.setStandardButtons(QMessageBox.Ok)
                mboxe.exec_()
                flag=1
            if flag:
                self.textbox1.setText(self.retmessage1)
            #print("Val is "+ etree.tostring(root, pretty_print=True).decode())
            mbox.setDetailedText(self.retmessage)
            mbox.setStandardButtons(QMessageBox.Ok)
            mbox.exec_()

    def getc(self):
        sourceobj=self.sender()
        if sourceobj.objectName() == "CUSTOM":
            self.customfilter = self.xmlbox.toPlainText()
        else:
            self.customfilter = None
        if self.yangcbox.isChecked():
            if self.yangcombobox2.currentText() is None:
                #print("Calling getconfig with " + self.yangcombobox1.currentText())
                worker = GWorker(self.Device.get, mode="Getconfig", ykey=self.yangcombobox1.currentText(),ykey2=None,outdir=self.ddir,filterstring=self.customfilter)
            else:
                #print("Calling getconfig with " + self.yangcombobox1.currentText() + " and " + self.yangcombobox2.currentText() )
                worker = GWorker(self.Device.get, mode="Getconfig", ykey=self.yangcombobox1.currentText(),ykey2=self.yangcombobox2.currentText(),outdir=self.ddir,filterstring=self.customfilter)
            self.threadpool.start(worker)
            self.w1.setEnabled(False)
            blockmsg = "Please wait, processing GET CONFIG request"
            self.blockerUI1.setText(blockmsg)
            self.blockerUI1.show()
            worker.signals.finished.connect(self.closeMyGLoop)
            worker.signals.result.connect(self.goAheadWithGetC)
        else:
            #print("Calling getc with " + self.yangcombobox.currentText())
            worker = GWorker(self.Device.get, mode="Getconfig", ykey=self.yangcombobox.currentText(),ykey2=None, outdir=self.ddir,filterstring=self.customfilter)
            self.threadpool.start(worker)
            self.w1.setEnabled(False)
            blockmsg = "Please wait, processing GET CONFIG request"
            self.blockerUI1.setText(blockmsg)
            self.blockerUI1.show()
            worker.signals.finished.connect(self.closeMyGLoop)
            worker.signals.result.connect(self.goAheadWithGetC)

    def goAheadWithGetC(self,status,message=None,message1=None):
        flag=0
        self.customfilter = None
        self.retstatus = status
        self.retmessage = message
        self.retmessage1 = message1
        if status:
            mbox = QMessageBox(self.w1)
            mbox.setWindowTitle("ERROR MESSAGE")
            mbox.setIcon(QMessageBox.Warning)
            mbox.setText("Error encountered on get operation")
            mbox.setDetailedText(self.retmessage)
            mbox.setStandardButtons(QMessageBox.Ok)
            mbox.exec_()
        else:
            mbox = QMessageBox(self.w1)
            mbox.setWindowTitle("NC MESSAGE")
            mbox.setIcon(QMessageBox.Information)
            mbox.setText("Output available click on details for filename")
            self.retmessage=self.retmessage+".xml"
            try:
                root = etree.fromstring(bytes(self.retmessage1,encoding='utf-8'))
                self.textbox1.setText(etree.tostring(root, pretty_print=True).decode())
            except Exception as e:
                mboxe = QMessageBox(self.w1)
                mboxe.setWindowTitle("ERROR MESSAGE")
                mboxe.setIcon(QMessageBox.Warning)
                mboxe.setText("Unable to pretty print XML output")
                mboxe.setDetailedText(str(e))
                mboxe.setStandardButtons(QMessageBox.Ok)
                mboxe.exec_()
                flag=1
            if flag:
                self.textbox1.setText(self.retmessage1)
            mbox.setDetailedText(self.retmessage)
            mbox.setStandardButtons(QMessageBox.Ok)
            mbox.exec_()

    def about(self):
        mbox = QMessageBox(self.w)
        mbox.setWindowTitle("About")
        mbox.setIcon(QMessageBox.Information)
        mbox.setText('''Copyright 2020 Nithin Karunakar
        
Powered by NCClient

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
''')
        mbox.setStandardButtons(QMessageBox.Ok)
        mbox.exec_()

    def getDir(self):
        #dialog = QFileDialog(w)
        self.dir = QFileDialog.getExistingDirectory(self.w, "Open Directory", "C:\\",QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        self.ldir_lineedit.setText(self.dir)

    def toggleLdir(self):
        if self.ldircbox.isChecked():
            self.ldirbtn.setEnabled(False)
            self.dir = self.Device.getDefaultYPath
            self.ldir_lineedit.setText(self.dir)
        else:
            self.ldirbtn.setEnabled(True)

    def getDoopDir(self):
        self.ddir = QFileDialog.getExistingDirectory(self.w, "Open Directory", "C:\\",QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        self.doop_lineedit.setText(self.ddir)

    def toggleDoopDir(self):
        if self.doopcbox.isChecked():
            self.ddirbtn.setEnabled(False)
            self.ddir = self.Device.getDefaultYPath
            self.doop_lineedit.setText(self.ddir)
        else:
            self.ddirbtn.setEnabled(True)

    def toggleInput(self):
        sourceobj=self.sender()
        if sourceobj.isChecked():
            self.savedbuttons[sourceobj].setEnabled(False)
        else:
            self.savedbuttons[sourceobj].setEnabled(True)

    def toggleyangCbox(self):
        if self.yangcbox.isChecked():
            self.yangcombobox.setEnabled(False)
            self.yangcombobox1.setEnabled(True)
            self.yangcombobox2.setEnabled(True)
        else:
            self.yangcombobox.setEnabled(True)
            self.yangcombobox1.setEnabled(False)
            self.yangcombobox2.setEnabled(False)
    
    def populatecbox2(self):
        self.yangcombobox2.clear()
        if self.yangcbox.isChecked():
            selyang=self.yangcombobox1.currentText()
        else:
            selyang=self.yangcombobox.currentText()
        if self.Device.getAugStatus(selyang):
            for c in self.Device.getAllAugLeafs(selyang):
                self.yangcombobox2.addItem(c)
        else:
            for c in self.Device.getAllUses(selyang):
                self.yangcombobox2.addItem(c)


class Worker(QRunnable):
    def __init__(self, targetf,args):
        super(Worker, self).__init__()
        self.fn=targetf
        self.args=args
        self.signals = WorkerSignals()

    def run(self):
        status=message=message1=None

        status,message, *rest = self.fn(self.args)
        if rest:
            message1=rest[0]
        self.signals.finished.emit()
        self.signals.result.emit(status,message,message1)

class GWorker(QRunnable):
    def __init__(self, targetf,**kwargs):
        super(GWorker, self).__init__()
        self.fn=targetf
        self.kdicts=kwargs
        self.signals = WorkerSignals()

    def run(self):
        status=message=message1=None
        status,message,message1 = self.fn(self.kdicts.pop('mode'),self.kdicts.pop('ykey'),self.kdicts.pop('ykey2'),self.kdicts.pop('outdir'),self.kdicts.pop('filterstring'))
        self.signals.finished.emit()
        self.signals.result.emit(status,message,message1)

class WorkerSignals(QObject):
    finished = pyqtSignal()
    result = pyqtSignal(int,str,str)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    nc=NCMenu()
