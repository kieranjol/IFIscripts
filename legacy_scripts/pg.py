#!/usr/bin/env python
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
        self.filmPreparationListBox.itemSelectionChanged.connect(self.getPrepList)
        self.filmCaptureInterventionsListBox.itemSelectionChanged.connect(self.getInterventionList)
        self.rawAudioInterventions.itemSelectionChanged.connect(self.getRawAudioInterventionsList)
        self.tapeWorkstationComboBox.activated[str].connect(self.getWorkstation)
        self.processButton.clicked.connect(self.closeIt)
        
        
    def closeIt(self): 
            self.close()     
    def getWorkstation(self):
        global tapeWorkstation
        tapeWorkstation = self.tapeWorkstationComboBox.currentText()    

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
        
    def getRawAudioInterventionsList(self):
        global rawAudiointerventions
        rawAudiointerventions = []
        
        rawAudiointerventionsObjects = self.rawAudioInterventions.selectedItems()
        for i in rawAudiointerventionsObjects:
            rawAudiointerventions.append(str(i.text()))
        return rawAudiointerventions
        
    def encode(self):
        global ifi_identifiersDict
        ifi_identifiersDict = {}
        user = self.userComboBox.currentText()
        oe = self.oeTextBox.toPlainText()
        filmographic = self.FilmographicTextBox.toPlainText()
        sourceAccession = self.sourceAccessionTextBox.toPlainText()
        #interventions = self.getInterventionList
        #items = self.getPrepLists
        
        
        if self.tabWidget.currentIndex() == 0:
            ifi_identifiersDict = {"workflow":"scanning","oe":str(oe), "filmographic":str(filmographic), "sourceAccession":str(sourceAccession), "interventions":interventions, "prepList":items, "user":str(user)}
            
        if self.tabWidget.currentIndex() == 1:
            ifi_identifiersDict = {"workflow":"tape", "oe":str(oe), "filmographic":str(filmographic), "sourceAccession":str(sourceAccession), "tapeWorkstation":str(tapeWorkstation)}
            
        elif self.tabWidget.currentIndex() == 2:
            ifi_identifiersDict = {"workflow":"rawaudio","oe":str(oe), "filmographic":str(filmographic), "sourceAccession":str(sourceAccession), "rawAudiointerventions":str(rawAudiointerventions)}
              
        return ifi_identifiersDict
        
        #items = self.getPrepList
        
        
        
def main():

    app = QtGui.QApplication(sys.argv)  # A new instance of QApplication
    form = ExampleApp()  # We set the form to be our ExampleApp (design)
    form.show()  # Show the form
    app.exec_()  # and execute the app
    
    return ifi_identifiersDict
    
if __name__ == '__main__':
    main()  # run the main function