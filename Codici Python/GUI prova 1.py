import sys
import pandas as pd
import time
import logging
import serial
import serial.tools.list_ports
import struct 
import numpy as np
import struct
from time import sleep
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from scipy.signal import butter, lfilter, freqs, find_peaks, hilbert, chirp
import math
from sklearn.preprocessing import StandardScaler
import os
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThreadPool, QRunnable, pyqtSlot,QSize, QRect, QTimer,QDateTime
from PyQt5.QtWidgets import (
    QApplication, QLabel,QStyle,QTextEdit,QMainWindow,QPushButton,QVBoxLayout,QWidget,QHBoxLayout,QComboBox,QHBoxLayout,QTabWidget,QCheckBox, QMessageBox, QLineEdit, QFileDialog,QSpinBox,QButtonGroup,QAbstractButton
)

#VARIABILI GLOBALI
CONN_STATUS =False #stato connessione porta
RX_DATA = False #stato ricezione dati
PORTA_SERIALE = 0
PAR_ARDUINO = False
logging.basicConfig(format="%(message)s", level=logging.INFO)

######################### 
# SERIAL_WORKER_SIGNALS #
#########################
class SerialWorkerSignals(QObject):
    """!
    @brief Class that defines the signals available to a serialworker.

    Available signals (with respective inputs) are:
        - device_port (classe): 
            str --> port name to which a device is connected
        - status:
            str --> port name
            int --> macro representing the state (0 - error during opening, 1 - success)
    """
    device_port = pyqtSignal(str)
    status = pyqtSignal(str, int)


################# 
# SERIAL_WORKER #
#################
class SerialWorker(QRunnable):
    """!
    @brief Main class for serial communication: handles connection with device.
    """
    def __init__(self, serial_port_name):
        """!
        @brief Init worker.
        """
        self.is_killed = False 
        super().__init__()
        self.port = serial.Serial()
        self.port_name = serial_port_name
        self.baudrate = 9600 # hard coded but can be a global variable, or an input param
        self.signals = SerialWorkerSignals()

    @pyqtSlot()
    def run(self):
        """!
        @brief Estabilish connection with desired serial port.
        """
        global CONN_STATUS
        global PORTA_SERIALE
        if not CONN_STATUS:
            try:
                self.port = serial.Serial(port=self.port_name, baudrate=self.baudrate,
                                        write_timeout=0, timeout=2)                
                if self.port.is_open:
                    CONN_STATUS = True
                    PORTA_SERIALE = self.port
                    self.signals.status.emit(self.port_name, 1)
                    logging.info("Connected with port {}.".format(self.port_name))
                    time.sleep(0.01)     
            
            except serial.SerialException:
                logging.info("Error with port {}.".format(self.port_name))
                #emetto il segnale status --> dal thread parallelo a quello principale                
                self.signals.status.emit(self.port_name, 0)
                time.sleep(0.01)

    @pyqtSlot()
    def send(self, char):
        """!
        @brief Basic function to send a single char on serial port.
        """
        try:
            self.port.write(char.encode('utf-8'))
            logging.info("Written {} on port {}.".format(char, self.port_name))
        except:
            logging.info("Could not write {} on port {}.".format(char, self.port_name))

    @pyqtSlot()
    def killed(self):
        global CONN_STATUS
        if self.is_killed and CONN_STATUS:
            self.port.close()
            time.sleep(0.01)
            CONN_STATUS= False
            self.signals.device_port.emit(self.port_name)
            logging.info("Killing the process")




'''MAIN WINDOW'''
class Window(QMainWindow):  
      
    def __init__(self):
        self.serial_worker = SerialWorker (None)
        #self.rx_worker = WorkerRXCOM()
        #self.signals = WorkerRXCOMSignals()
        #self.setup_data = WorkerRXCOMSetup()
        #self.setup_signals = WorkerRXCOMSetupSignals()
        super(Window,self).__init__()
        self.threadpool = QThreadPool()
        self.connected =CONN_STATUS
        self.serialscan()
        self.setupUi()
        self.active_folder = 'C:\\Acquisizioni\\'

    def setupUi(self):
        #GENERAL SETTINGS
        self.setStyleSheet("font-size: 14pt;")
        self.setFont(QtGui.QFont("Arial"))
        self.setWindowTitle("Wearable EIT")
        #self.setWindowIcon(QtGui.QIcon('logo.png'))

        #BUTTONS
        self.new_upload_btn=QPushButton(
            text="Upload a new EIT file",
            clicked=self.new_file
        )
        self.new_upload_btn.setStyleSheet("background-color: rgb(255,204,204);")
        #self.new_upload_btn.setFixedHeight(100)

        self.TestoRX = QTextEdit(self)
        self.TestoRX.setFixedHeight(700)

        self.transmit_btn = QPushButton(
            text=("Start Transmission"), 
            checkable=True,
            toggled=self.transmit
        )
        #self.transmit_btn.setIconSize(QSize(70,70))
        self.transmit_btn.setFixedHeight(100)
        self.transmit_btn.setStyleSheet("background-color: rgb(51,255,51);")
        #self.transmit_btn.setIcon(QtGui.QIcon('bluetooth (2).png'))

        self.clear_text_btn = QPushButton(
            text = ("Clear Data"),
            clicked = self.clear_data
        )
        self.clear_text_btn.setStyleSheet("background-color: rgb(160,160,160);")
        #self.clear_text_btn.setIcon(QtGui.QIcon('eraser.png'))
        #self.clear_text_btn.setIconSize(QSize(70,70))
        self.clear_text_btn.setFixedHeight(100)

        self.send_parameters_btn = QPushButton(
            text = ("Confirm Parameters"),
            clicked = self.confirm_parameters
        )
        #self.send_parameters_btn.setFixedSize(500,80)
        #self.send_parameters_btn.setIcon(QtGui.QIcon('check.png'))
        #self.send_parameters_btn.setIconSize(QSize(70,70))

        self.import_file_btn = QPushButton(
            text= "Import file",
            clicked = self.import_file
        )
        #self.import_file_btn.setStyleSheet("background-color: rgb(255,204,204);")
        #self.import_file_btn.setIcon(QtGui.QIcon('import.png'))
        #self.import_file_btn.setIconSize(QSize(150,150))
        #self.import_file_btn.setFixedSize(600,400)

        self.export_file_btn = QPushButton(
            text = "Export file",
            clicked = self.export_file
        )
        #self.export_file_btn.setStyleSheet("background-color: rgb(204,229,255);")
        #self.export_file_btn.setIcon(QtGui.QIcon('export.png'))
        #self.export_file_btn.setIconSize(QSize(150,150))
        #self.export_file_btn.setFixedSize(600,400)    


        #LAYOUTS
        #Layout TRANSMISSION TAB
        self.layout_graph = QVBoxLayout()
        #self.layout_graph.addWidget(self.AccAxisPlotWidget)
        #self.layout_graph.addWidget(self.AccModPlotWidget)
        self.layout_rx1 = QHBoxLayout()
        self.layout_rx2 = QVBoxLayout()
        self.layout_rx3 = QHBoxLayout()
        self.layout_rx = QHBoxLayout()
        self.label_time = QLabel()
        self.label_time.setText("Acquisition duration: ")
        self.label_time.setFixedSize(200,50)
        self.text_time = QTextEdit()
        self.text_time.setFixedSize(100,50)
        self.text_time.setReadOnly(True)
        self.stringa = ""
        self.layout_rx1.addWidget(self.transmit_btn)
        #self.layout_rx1.addWidget(self.new_acquisition_btn_rx)
        self.layout_rx1.addWidget(self.clear_text_btn)
        self.layout_rx3.addWidget(self.label_time, alignment=Qt.AlignRight)
        self.layout_rx3.addWidget(self.text_time)
        self.layout_rx2.addWidget(self.TestoRX)
        self.layout_rx2.addLayout(self.layout_rx3)
        self.layout_rx2.addLayout(self.layout_rx1)
        self.layout_rx.addLayout(self.layout_rx2) 
        self.layout_rx.addLayout(self.layout_graph) 
        self.widget_rx = QWidget()
        self.widget_rx.setLayout(self.layout_rx)

        #Layout MODALITY AND PARAMETERS SELECTION TAB: acquisition protocol, number electrodes, algorithm to use, time acquisition, 2D vs 3D, fdEIT vs tdEIT
        #protocollo
        self.box_protocol= QComboBox()
        self.box_protocol.addItems(["Adjacent", "Polar", "Zig-Zag"])    
        self.box_protocol.activated.connect(self.check_index_protocol)
        #self.box_protocol.setFixedSize(100,50)

        #n_el
        self.box_electrodes = QComboBox()
        self.box_electrodes.addItems(["8", "16", "32", "64"])   
        #self.box_electrodes.setFixedSize(100,50) 
        self.box_electrodes.activated.connect(self.check_index_electrodes)

        #acquisition time
        self.spin_minutes = QSpinBox(self)
        self.spin_minutes.setRange(1, 59)
        self.spin_minutes.lineEdit().setReadOnly(True)
        self.spin_minutes.setSizeIncrement(1,1)
        #self.spin_minutes.setFixedSize(100,50)
        self.spin_minutes.setSuffix(" min")
        self.spin_minutes.valueChanged.connect(self.update_time)

        self.protocol_label = QLabel()
        self.electrode_label = QLabel()
        self.min_label = QLabel()
        self.protocol_label.setText("Select Acquisition Protocol:")
        #self.protocol_label.setFixedSize(200,50)
        #self.electrode_label.setFixedSize(200,50)
        self.electrode_label.setText("Select Number Electrodes:")
        #self.min_label.setFixedSize(200,50)
        self.min_label.setText("Acquisition time:")


        self.layout_botton_1 = QHBoxLayout()
        self.b1 = QCheckBox("2D")
        self.b1.setChecked(True)
        self.b1.stateChanged.connect(lambda:self.btnstate(self.b1))
        self.layout_botton_1.addWidget(self.b1)
        self.b2 = QCheckBox("3D")
        self.b2.toggled.connect(lambda:self.btnstate(self.b2))
        self.layout_botton_1.addWidget(self.b2)
        self.bg = QButtonGroup()
        self.bg.addButton(self.b1,1)
        self.bg.addButton(self.b2,2)
        self.bg.buttonClicked[QAbstractButton].connect(self.btngroup)

        self.layout_botton_2 = QHBoxLayout()
        self.b3 = QCheckBox("fEIT")
        self.b3.setChecked(True)
        self.b3.stateChanged.connect(lambda:self.btnstate(self.b3))
        self.layout_botton_2.addWidget(self.b3)
        self.b4 = QCheckBox("tdEIT")
        self.b4.toggled.connect(lambda:self.btnstate(self.b4))
        self.layout_botton_2.addWidget(self.b4)
        self.bg1 = QButtonGroup()
        self.bg1.addButton(self.b3,1)
        self.bg1.addButton(self.b4,2)
        self.bg1.buttonClicked[QAbstractButton].connect(self.btngroup)

        self.layout_parameters_bg=QVBoxLayout()
        self.layout_parameters_bg.addLayout(self.layout_botton_1)
        self.layout_parameters_bg.addLayout(self.layout_botton_2)
                
        self.layout_parameters_protocol_box = QHBoxLayout()
        self.layout_parameters_protocol_box.addWidget(self.protocol_label)
        self.layout_parameters_protocol_box.addWidget(self.box_protocol)

        self.layout_parameters_electr_box = QHBoxLayout()
        self.layout_parameters_electr_box.addWidget(self.electrode_label)        
        self.layout_parameters_electr_box.addWidget(self.box_electrodes)

        self.layout_parameters_time_min = QHBoxLayout()
        self.layout_parameters_time_min.addWidget(self.min_label)
        self.layout_parameters_time_min.addWidget(self.spin_minutes)
        self.layout_parameters_time_sec = QHBoxLayout()   

        self.layout_parameters = QVBoxLayout()
        #self.layout_parameters.addWidget(self.setting_exp_checkbox,alignment=Qt.AlignCenter )
        self.layout_parameters.addLayout(self.layout_parameters_bg)
        self.layout_parameters.addLayout(self.layout_parameters_protocol_box)
        self.layout_parameters.addLayout(self.layout_parameters_electr_box)
        self.layout_parameters.addLayout(self.layout_parameters_time_min)
        self.layout_parameters.addLayout(self.layout_parameters_time_sec)
        self.layout_parameters.addWidget(self.send_parameters_btn, alignment=Qt.AlignCenter)

        self.layout_settings_main = QVBoxLayout()
        self.widget_settings_main = QWidget()
        #self.widget_settings_main.setLayout(self.layout_parameters)
        self.protocol=0
        self.electrodes=0
        self.modality=0 

        #Layout HOME TAB
        self.layout_port = QHBoxLayout()
        self.layout_port1 = QVBoxLayout()
        self.label_port = QLabel()
        self.label_port.setText("Please connect your device:")
        #self.label_port.setStyleSheet("font-size: 15pt;")
        self.layout_port.addWidget(self.label_port)
        self.layout_port.addWidget(self.com_list_widget)
        self.layout_port.addWidget(self.conn_btn)
        #self.layout_port1.addWidget(self.image_logo, alignment = Qt.AlignHCenter)
        self.layout_port1.addLayout(self.layout_port)
        self.layout_port1.addLayout(self.layout_parameters)
        self.conn_btn.setStyleSheet("background-color: rgb(153,204,255)")
        self.widget_port = QWidget()
        self.widget_port.setLayout(self.layout_port1)


        #Layout IMPORT EXPORT FILE
        self.layout_import_file = QVBoxLayout()
        #self.label_import_file = QLabel("Upload EIT data")
        #self.layout_import_file.addWidget(self.label_import_file)
        self.layout_import_file.addWidget(self.import_file_btn)
        self.layout_export_file = QVBoxLayout()
        self.layout_export_file_2 = QVBoxLayout()
        #self.label_export_file = QLabel("Download EIT data")
        #self.layout_export_file_2.addWidget(self.label_export_file)
        #self.layout_export_file.addLayout(self.layout_export_file_2)
        self.layout_export_file.addWidget(self.export_file_btn)

        self.layout_file = QHBoxLayout()
        self.layout_file.addLayout(self.layout_import_file)
        self.layout_file.addLayout(self.layout_export_file)
        self.export_file_btn.setEnabled(False)
        self.widget_file = QWidget()
        self.widget_file.setLayout(self.layout_file)

        #TABS LAYOUT
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(False)
        self.tabs.addTab(self.widget_port,"CONNECTION")
        self.tabs.addTab(self.widget_file, "DOWNLOAD/UPLOAD")
        #self.tabs.addTab(self.widget_settings_main,"Settings")
        self.tabs.addTab(self.widget_rx, "LIVE EIT")
        self.setCentralWidget(self.tabs)
        self.tabs.setCurrentIndex(0)

        #INITIAL SETUP
        #self.tabs.setTabEnabled(2,False)
        #self.tabs.setTabEnabled(3,False)
        #self.tabs.setTabEnabled(4,False)
        #self.tabs.setTabEnabled(5,False)
    
    #FUNZIONE CHECK BOTTONI
    def btnstate(self,b):
        if b.isChecked() == True:
            if b.text()=="2D": 
                self.dimension=0 #2D acquisition
                print("2D acquisition mode")
            elif b.text()=="3D": 
                self.dimension=1 #3D acquisition
                print("3D acquisition mode")
            elif b.text()=="fEIT":
                self.eit_modality=0
            elif b.text()=="tdEIT":
                self.eit_modality=1

    def btngroup(self,btn):
        print (btn.text() +" is selected")

    #FUNZIONI PER IMPORT/EXPORT FILE
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Text file (*.txt)", options=options)
        if self.fileName:
            print(self.fileName)
    
    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","Text file (*.txt)", options=options)
        if self.fileName:
            print(self.fileName)

    def import_file (self):
        self.openFileNameDialog()
        f=open(self.fileName)
        info=pd.read_csv(f,sep=',', header=0, decimal='.',engine='python')
        info=info.iloc[0:1,:]
        #import of the parameters accordingly to the order in the saved file 
        #self.IDsubject = info.iloc[0,0]
        #self.time_stamp=info.iloc[0,1]
        #self.frequency=int(info.iloc[0,2])
        #self.time_interval=info.iloc[0,3]
        #print(info.shape)
        #if info.shape==(1, 5):
        #    self.modality=info.iloc[0,4]
        #if (self.time_interval%60)==0:
        #   self.data_buffer = np.append(self.data_buffer, np.power(np.power(self.acc_x[i],2)+np.power(self.acc_y[i],2)+np.power(self.acc_z[i],2),0.5))
        self.tabs.setTabEnabled(4,True)
        self.breathing_offline()

    def export_file (self):
        self.fileName = self.time_stamp
        #print(self.fileName)
        path = os.path.join(self.active_folder, self.fileName)
        self.fileName, _ = QFileDialog.getSaveFileName(self, "Save File", path, "(*.csv)")
        self.active_folder = os.path.dirname(self.fileName)
        if ".txt" in self.fileName:
            data_file=open(self.fileName,'w')
        else:
            data_file=open(self.fileName + ".txt",'w')

        #self.export_time_acquisition=self.max_time_acquisition
        #acc_data_array = "ID,TIME,FREQUENCY,DURATION,MODALITY\n"
        #acc_data_array+= "{},{},{},{},{}\n".format(self.IDsubject,self.time_stamp,self.frequency,self.export_time_acquisition,self.modality)
        #acc_data_array+= "X,Y,Z\n"
        #self.acc_data_txt=self.acc_data_txt
        data_array="" #header
        data_array = data_array + self.data_txt #header+data
        data_file.write(data_array)
        data_file.close()
        self.data_txt = ""

    def check_index_protocol(self):
        self.protocol=self.box_protocol.currentIndex()
        print(self.FS)
        
    def check_index_electrodes(self):
        self.electrodes=self.box_electrodes.currentIndex()
        print(self.electrodes)
        self.n_el = self.electrodes 

    def confirm_parameters(self):
        global SETTINGS
        global PORTA_SERIALE
        SETTINGS=1
        #self.tabs.setTabEnabled(3,True)
        self.max_time_acquisition = self.spin_minutes.value()*60
        #byte_parametri = ((self.protocol<<4)|(self.electrodes)) #da far interpretare firmware
        #PORTA_SERIALE.write(b'a') 
        #PORTA_SERIALE.write(struct.pack('<H', byte_parametri)) 

    def update_time(self):
        self.max_time_acquisition = self.spin_minutes.value()*60        

    def clear_data(self):
        self.TestoRX.clear()
        self.stringa = ""
        self.data_txt=""

    #PORT SCAN FUNCTION
    def serialscan(self):
        self.port_text = ""
        self.com_list_widget = QComboBox()
        #self.com_list_widget.setFixedSize(400,100)
        self.com_list_widget.currentTextChanged.connect(self.port_changed)

        self.conn_btn =QPushButton(
            text = ("Connect to port: {}".format(self.port_text)),
            checkable = True,
            toggled = self.on_toggle
        )
        
        #self.conn_btn.setFixedSize(400,100)
        #self.conn_btn.setIcon(QtGui.QIcon('link.png'))
        #self.conn_btn.setIconSize(QSize(40, 40))
        serial_port = [
            p.name
            for p in serial.tools.list_ports.comports()
        ]
        self.com_list_widget.addItems(serial_port)

    def port_changed(self):
        self.port_text =self.com_list_widget.currentText()
        self.conn_btn.setText("Connect to port {}".format(self.port_text))
    
    @pyqtSlot(bool)
    def on_toggle(self, checked):
        """!
        @brief Allow connection and disconnection from selected serial port.
        """
        if checked:
            # setup reading worker
            self.conn_btn.setStyleSheet("background-color: rgb(153,255,153)")
            self.serial_worker = SerialWorker(self.port_text) # needs to be re defined
            # connect worker signals to functions
            self.serial_worker.signals.status.connect(self.check_serialport_status)
            self.serial_worker.signals.device_port.connect(self.connected_device)
            # execute the worker
            self.threadpool.start(self.serial_worker)
            #self.serial_worker.signals.setup.connect(self.print_EEPROM_setup)
            self.com_list_widget.setDisabled(True)

        else:
            self.conn_btn.setStyleSheet("background-color: rgb(153,204,255)")
            self.conn_btn.setChecked(False)
            #self.tabs.setCurrentIndex(0)
            #self.tabs.setTabEnabled(1,True)
            #self.tabs.setTabEnabled(2,False)
            #self.tabs.setTabEnabled(3,False)
            #self.tabs.setTabEnabled(4,False)

            #self.transmit_btn.setText("START Transmission")
            #self.transmit_btn.setStyleSheet("background-color: rgb(51,255,51);")
            #self.transmit_btn.setIcon(QtGui.QIcon('bluetooth (2).png'))
            #self.timer.stop()
            #self.timer_acquisition.stop()
            RX_DATA = False
            self.com_list_widget.show()
            #self.acquisition_time = 0
            #self.text_time.setText("00:00")
            #self.statistics_btn.setEnabled(True) 
            #self.new_acquisition_btn.setEnabled(False)
            #self.new_acquisition_btn_rx.setEnabled(False)
            #stop the transmission
            #if PORTA_SERIALE!=0:    
                #PORTA_SERIALE.write(b't')
            
            time.sleep(0.1)

            # kill thread
            self.serial_worker.is_killed = True
            self.serial_worker.killed()
            self.com_list_widget.setDisabled(False) # enable the possibility to change port
            self.conn_btn.setText(
                "Connect to port {}".format(self.port_text)
            )
            #self.reset_GUI()
            
    def check_serialport_status(self, port_name, status):
        """!
        @brief Handle the status of the serial port connection.

        Available status:
            - 0  --> Error during opening of serial port
            - 1  --> Serial port opened correctly
        """
        if status == 0:
            self.com_list_widget.setEnabled(True)
            self.conn_btn.setChecked(False)

        elif status == 1: #successful connection
            self.tabs.setTabEnabled(2,True)
            self.conn_btn.setText(
                "Disconnect from port {}".format(port_name)
            )

    def connected_device(self, port_name):
        """!
        @brief Checks on the termination of the serial worker.
        """
        logging.info("Port {} closed.".format(port_name))

    def transmit(self, checked):
        """!
        @brief Allow connection and disconnection from selected serial port.
        """

        if checked:
            self.transmit_btn.setText("STOP Transmission")
            #self.transmit_btn.setStyleSheet("background-color: rgb(255,51,51);")
            #self.transmit_btn.setIcon(QtGui.QIcon('bluetooth.png'))
            #if self.finished==False:
            self.start_transmission()
            
        else:
            self.transmit_btn.setText("START Transmission")
            self.transmit_btn.setStyleSheet("background-color: rgb(51,255,51);")
            #self.transmit_btn.setIcon(QtGui.QIcon('bluetooth (2).png'))

    def stop_transmission(self):
        self.transmit_btn.setText("START Transmission")
        self.transmit_btn.setStyleSheet("background-color: rgb(51,255,51);")
        #self.transmit_btn.setIcon(QtGui.QIcon('bluetooth (2).png'))
        self.timer.stop()
        self.timer_acquisition.stop()
        #PORTA_SERIALE.write(b's')
        RX_DATA = False
        self.com_list_widget.show()
        #self.statistics_btn.setEnabled(True)
        #self.new_acquisition_btn_rx.setEnabled(True)
        #self.new_acquisition_btn.setEnabled(True)

    def start_transmission(self): 
        global RX_DATA
        global PORTA_SERIALE
        self.export_file_btn.setEnabled(True) 
        #if(self.eit_modality==0):
        #    PORTA_SERIALE.write(b'f') #'a' interpretata da arduino come fEIT
        #else:
        #    PORTA_SERIALE.write(b't') #'b' interpretata da arduino come tdEIT
        #time.sleep(1)
        PORTA_SERIALE.write(b'a')
        time.sleep(10)
        RX_DATA = True
        #Start the thread for the reception of data from arduino
        #self.rx_worker = WorkerRXCOM() #prima dichiaro rx_worker e subito dopo connetto i segnali
        #self.threadpool.start(self.rx_worker) #start threadpool
        #self.rx_worker.signals.dati_accelerazione.connect(self.display_raw_data)
        #self.rx_worker.signals.dati_accelerazione.connect(self.raw_data_plot)
        #
        #self.timer.start(int(self.time_interval)*1000)
        #self.timer_acquisition.start(1000)
        #now = QDateTime.currentDateTime()
        #self.time_stamp = now.toString("dd-MM-yyyy_HH-mm-ss")
        #print(self.time_stamp)
        #self.num = 0
        #self.minutes = 0
        #self.statistics_btn.setEnabled(False) #disabilito il pulsante che verrà abilitato una volta conclusa la trasmissione
        #self.new_acquisition_btn_rx.setEnabled(False)
        #self.new_acquisition_btn.setEnabled(False)
        #self.tabs.setTabEnabled(2,False)
        #while RX_DATA:
        #if PORTA_SERIALE.in_waiting>343 :
        dataArray = PORTA_SERIALE.read(164)
        dataArray = struct.unpack('164B',dataArray)
        dataArray = np.asarray(dataArray,dtype=np.uint8)
        lastIndex = len(dataArray)-1
        #if dataArray[0]==10 and dataArray[lastIndex]==11: #10 = 0A, 11 = 0B
        #imp_data=dataArray[1:171]
        print("Bytes ricevuti: {}\nNumero bytes ricevuti: {}".format(dataArray, len(dataArray)))
        #print(len(dataArray))
        #RX_DATA=False
        #else:
        #    RX_DATA=False
        #    print("Wrong header")
        dataFloat = struct.unpack('41f',dataArray)
        dataFloat = np.asarray(dataFloat)#,dtype=float)
        print("Dati ricevuti: {}\nNumero dati ricevuti: {}".format(dataFloat, len(dataFloat)))
        print("Finished!")



    def display_time(self):
            self.acquisition_time += 1 
            minutes = int(self.acquisition_time/60)
            seconds = int(self.acquisition_time%60)
            self.text_time.setText("{:02d}:{:02d}".format(minutes, seconds))
            if (self.acquisition_time == self.max_time_acquisition):
                self.transmit_btn.setEnabled(False)
                self.finished=True
                self.transmit_btn.setChecked(False)
                self.stop_transmission()
                self.acquisition_time = 0
                self.text_time.setText("00:00")
                self.finished=False

    def new_acquisition(self):
        self.tabs.setTabEnabled(2,True)
        self.tabs.setTabEnabled(3,False)
        self.tabs.setTabEnabled(4,False)
        #self.tabs.setTabEnabled(5,False)
        #self.reset_GUI()
        self.tabs.setCurrentIndex(2)


    def new_file(self):
        self.tabs.setTabEnabled(2,False)
        self.tabs.setTabEnabled(3,False)
        self.tabs.setTabEnabled(4,False)
        #self.tabs.setTabEnabled(5,False)
        #self.reset_GUI()
        self.tabs.setCurrentIndex(1)


    def ExitHandler(self):
            """!
            @brief Kill every possible running thread upon exiting application.
            """
            global PORTA_SERIALE
            #if(PORTA_SERIALE!=0 and PORTA_SERIALE.is_open):
                #PORTA_SERIALE.write(b't')
                #time.sleep(0.1)
            self.serial_worker.is_killed = True
            self.serial_worker.killed()


app = QApplication(sys.argv)
win = Window()
app.aboutToQuit.connect(win.ExitHandler)
win.show()
sys.exit(app.exec())




    


 












