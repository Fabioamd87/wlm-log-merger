import os, sys
from xml.dom import minidom
from xml.dom.minidom import Document, ProcessingInstruction

from datetime import date

from PyQt4 import QtGui, QtCore
from gui import Ui_MainWindow

#from create_xml import new_message, new_invitation, new_invitation_response

DEST = 'Cronologia3'

class MainWindow(QtGui.QMainWindow):
    def __init__(self, win_parent = None):
        QtGui.QMainWindow.__init__(self, win_parent)
        self.vbox = QtGui.QVBoxLayout()
        self.hbox1 = QtGui.QHBoxLayout()
        self.vbox.addLayout(self.hbox1)

        self.source_label = QtGui.QLineEdit()
        self.source_button = QtGui.QPushButton('select source file')

        self.hbox1.addWidget(self.source_label)
        self.hbox1.addWidget(self.source_button)
       
        self.destination_label = QtGui.QLineEdit()
        self.destination_button = QtGui.QPushButton('select destination file')

        self.hbox2 = QtGui.QHBoxLayout()
        self.vbox.addLayout(self.hbox2)

        self.hbox2.addWidget(self.destination_label)
        self.hbox2.addWidget(self.destination_button)
        
class AbstractItem():
    """not used"""
    def __init__(self,text, date, time, datetime, ID, fromuser, touser, style):
        self.text = text
        self.date = date
        self.datetime = datetime
        self.ID = ID
        self.fromuser = fromuser
        self.touser = touser
        self.style = style

    def set_filenumber(self,n):
        self.filenumber = n

class msg_class():
    """not used"""
    def __init__(self,node, filenumber):
        self.node = node
        self.filenumber = filenumber
        d = self.node.attributes['Date'].value
        self.date = create_date_from_value(d)

class session_class():
    def __init__(self, messages):
        self.messages = messages
        d = messages[0].attributes['Date'].value
        self.date = create_date_from_value(d)
        #print('creating a session object with first message in date',self.date)

def create_date_from_value(value):
    day1 = int(value[0:2])
    month1 = int(value[3:5])
    year1 = int(value[6:10])    
    d = date(year1,month1,day1)
    #print('d1: ',day1,month1,year1)
    return d

def find_who_is_the_reference():
    """broken, I think"""
    
    item1 = msgs1.firstChild
    item2 = msgs2.firstChild

    d1 = item1.attributes['Date'].value
    d2 = item2.attributes['Date'].value

    d1 = create_date_from_value(d1)
    d2 = create_date_from_value(d2)

    if d1 < d2:        
        global LAST_ID_REF #global variable
        LAST_ID_REF = msgs1.lastChild.attributes['SessionID'].value
        print('ref is d1')
        return 1
    else:
        print('ref is d2')
        return 2

def add_messages_to_session_list(msgs, sessions):
    """called for each file messages it group by sessionID"""
    tmp = []
    i=1 #starting sessionID is 1
    for msg in msgs:
        actual = int(msg.attributes['SessionID'].value)
        if actual == i:    
            tmp.append(msg)
        else:
            sessions.append(tmp)
            tmp = []
            i=int(msg.attributes['SessionID'].value)
    #when done append tmp tupple to sessions tuple
    sessions.append(tmp)

def merge(File1, File2):
    Doc1 = minidom.parse(File1)
    Doc2 = minidom.parse(File2)
    Doc3 = Document()

    msgs1 = Doc1.getElementsByTagName('Log')[0]
    msgs2 = Doc2.getElementsByTagName('Log')[0]

    pi = ProcessingInstruction('xml-stylesheet', "type='text/xsl' href='MessageLog.xsl'")
    Doc3.appendChild(pi)

    Log3 = Doc3.createElement('Log')
    Log3.setAttribute("FirstSessionID", "1")
    #Log.setAttribute("LastSessionID", "1")
    Doc3.appendChild(Log3)

    print('len 1: ',len(msgs1.childNodes))
    print('len 2: ',len(msgs2.childNodes))

    #create a tuple of "tuples of messages"
    sessions = []
    add_messages_to_session_list(msgs1.childNodes, sessions)
    add_messages_to_session_list(msgs2.childNodes, sessions)
        
    #create an object that contain messages and date of the first message
    session_objects = []
    for s in sessions:
        if s:
            o = session_class(s)
            session_objects.append(o)

    #order this tuple by the first element (message) data attributes of each tuple contained
    print('sorting')
    session_objects.sort(key = lambda x: x.date)

    #create a new log by incrementing sessionIDs
    i=1
    for session in session_objects:
        for message in session.messages:
            message.attributes['SessionID'].value = str(i)
            Log3.appendChild(message)
        i+=1
    
    last_session_id = Log3.lastChild.attributes['SessionID'].value
    Log3.setAttribute("LastSessionID", last_session_id)

    print('writing file')
    if not os.path.exists(DEST):    
        os.mkdir(DEST)
    current_dir = os.getcwd()
    os.chdir(current_dir + '/'+ DEST)
    f = open(os.path.basename(File1),'w')
    f.write(Doc3.toxml())
    f.close()
    
#1(assumption that between first and last message of one session ID there isn't (cronologically) any message from other sessions ID, this can't be proven when you connect from multiple session and log from both session, but this kill the idea of one session ID (or maybe is handled?)

#2 we should avoid duplicated messages too (also caused by two simulteneous logging

class MyForm(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        QtCore.QObject.connect(self.ui.pushButton_2, QtCore.SIGNAL("clicked()"), self.on_first_clicked )
        QtCore.QObject.connect(self.ui.pushButton, QtCore.SIGNAL("clicked()"), self.on_second_clicked)
        QtCore.QObject.connect(self.ui.pushButton_3, QtCore.SIGNAL("clicked()"), self.on_merge_clicked)
     
    def on_first_clicked(self):
        File1 = QtGui.QFileDialog.getOpenFileName();
        self.ui.lineEdit_2.setText(File1)

    def on_second_clicked(self):
        File2 = QtGui.QFileDialog.getOpenFileName();
        self.ui.lineEdit.setText(File2)

    def on_merge_clicked(self):
        File1 = self.ui.lineEdit_2.text()
        File2 = self.ui.lineEdit.text()
        if File1 and File2:
            merge(File1, File2)
        else:
            print('specify a file')

    def add_entry(self):
        self.ui.lineEdit.selectAll()
        self.ui.lineEdit.cut()
        self.ui.textEdit.append("")
        self.ui.textEdit.paste()

def main():
    #if no argument start gui version
    if len(sys.argv) == 1:
        app = QtGui.QApplication(sys.argv)
        myapp = MyForm()
        myapp.show()
        sys.exit(app.exec_())

    #terminal usage
    if sys.argv[1]== "--help":
        print('Usage: merge_xml file1 file2')
        return

    if len(sys.argv) == 3:
        File1 = sys.argv[1]
        File2 = sys.argv[2]

        if os.path.basename(File1) != os.path.basename(File2):
            print('you are trying to merge logs from different contacts, quitting...')
            return
        else:
            merge(File1,File2)

if __name__ == "__main__":
    main()
