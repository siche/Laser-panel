# QDateTime dateTime = QDateTime::currentDateTime();
#    // 显示的内容
#    m_pLCD->display(dateTime.toString("yyyy-MM-dd HH:mm:ss.zzz"));

from PyQt5.QtWidgets import QApplication,QWidget,QPushButton,QGridLayout,QLCDNumber
from PyQt5 import QtCore
import sys
import time 

class time_count(QWidget):
    def __init__(self,parent=None):
        super(time_count, self).__init__(parent=None)
        self.initUi()
    
    def initUi(self):
        btn1 = QLCDNumber()
        btn1.setDigitCount(8)
        btn1.display("00:00:00")

        btn2 = QPushButton('Start')
        btn2.clicked.connect(self.start)
        btn3 = QPushButton('Reset')
        btn3.clicked.connect(self.reset)
        btn4 = QPushButton('Pause')
        btn4.clicked.connect(self.pause)

        layout = QGridLayout()
        layout.addWidget(btn1,1,0,1,2)
        layout.addWidget(btn2,1,2)
        layout.addWidget(btn4,1,3)
        layout.addWidget(btn3,1,4)
        self.setLayout(layout)
        self.btn1 = btn1
        self.btn2 = btn2
        
        self.initime = time.time()
        self.duration = 0
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh_time)
        
    def start(self):
        self.initime = time.time()
        self.timer.start(100)
    
    def refresh_time(self):
        self.duration = self.duration + time.time() - self.initime
        mins = self.duration // 60
        # print(mins)
        sec1 = self.duration % 60 
        sec2 = sec1 % 1
        time_str = "%02d:%02d.%02d" %(mins,sec1,100*sec2)
        self.btn1.display(time_str)
        self.initime = time.time()

    def reset(self):
        self.timer.stop()
        self.duration = 0
        self.btn1.display("00:00.00")

    def pause(self):
        self.timer.stop()

if __name__ =="__main__":
    app = QApplication(sys.argv)
    ex = time_count()
    ex.show()
    sys.exit(app.exec_())
        


