from PyQt4 import QtGui, QtCore
import sys
import subprocess
import premisgui
import os
import filecmp
import hashlib
from glob import glob




class ExampleApp(QtGui.QMainWindow, premisgui.Ui_MainWindow):
    def __init__(self):
        global text
        global counter
        counter = 0
        
        super(self.__class__, self).__init__()
        self.setupUi(self)  # This is defined in design.py file automatically
        self.processButton.setEnabled(True)
        self.processButton.clicked.connect(self.encode)
        #self.oeTextBox.textChanged.connect(self.countup)
        #print text
        #items = []
        self.filmPreparationListBox.itemClicked.connect(self.getPrepList)
        self.filmCaptureInterventionsListBox.itemClicked.connect(self.getInterventionList)
        
        

    def getPrepList(self):
        global items
        items = []
        
        itemObjects = self.filmPreparationListBox.selectedItems()
        for i in itemObjects:
            items.append(str(i.text()))
        return items
    
    def getInterventionList(self):
        global interventions
        interventions = []
        
        interventionsObjects = self.filmCaptureInterventionsListBox.selectedItems()
        for i in interventionsObjects:
            interventions.append(str(i.text()))
        return interventions
    def encode(self):
        
        oe = self.oeTextBox.toPlainText()
        filmographic = self.FilmographicTextBox.toPlainText()
        sourceAccession = self.sourceAccessionTextBox.toPlainText()
        print filmographic
        print sourceAccession
        
        
        print oe
        #items = self.getPrepList
        print items
        print interventions
        
def main():

    app = QtGui.QApplication(sys.argv)  # A new instance of QApplication
    form = ExampleApp()  # We set the form to be our ExampleApp (design)
    form.show()  # Show the form
    app.exec_()  # and execute the app
    return items
if __name__ == '__main__':
    main()  # run the main function