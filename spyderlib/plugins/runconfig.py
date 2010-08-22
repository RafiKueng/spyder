# -*- coding: utf-8 -*-
#
# Copyright © 2010 Pierre Raybaut
# Licensed under the terms of the MIT License
# (see spyderlib/__init__.py for details)

"""Run configurations related dialogs and widgets and data models"""

from PyQt4.QtGui import (QVBoxLayout, QFileDialog, QDialog, QWidget, QGroupBox,
                         QLabel, QPushButton, QCheckBox, QLineEdit, QComboBox,
                         QHBoxLayout, QDialogButtonBox, QStackedWidget,
                         QGridLayout, QSizePolicy, QRadioButton, QMessageBox)
from PyQt4.QtCore import SIGNAL, SLOT

import os, sys
import os.path as osp

# For debugging purpose:
STDOUT = sys.stdout

# Local imports
from spyderlib.config import get_icon, CONF
from spyderlib.utils.qthelpers import get_std_icon


class RunConfiguration(object):
    def __init__(self):
        self.args = ''
        self.args_enabled = False
        self.wdir = ''
        self.wdir_enabled = False
        self.current = False
        self.interact = False
        self.debug = False
        self.python_args = ''
        self.python_args_enabled = False
        
    def set(self, options):
        self.args = options.get('args', '')
        self.args_enabled = options.get('args/enabled', False)
        self.wdir = options.get('workdir', os.getcwdu())
        self.wdir_enabled = options.get('workdir/enabled', False)
        self.current = options.get('current', False)
        self.interact = options.get('interact', False)
        self.debug = options.get('debug', False)
        self.python_args = options.get('python_args', '')
        self.python_args_enabled = options.get('python_args/enabled', False)
        
    def get(self):
        return {
                'args/enabled': self.args_enabled,
                'args': self.args,
                'workdir/enabled': self.wdir_enabled,
                'workdir': self.wdir,
                'current': self.current,
                'interact': self.interact,
                'debug': self.debug,
                'python_args/enabled': self.python_args_enabled,
                'python_args': self.python_args,
                }
        
    def get_working_directory(self):
        if self.wdir_enabled:
            return self.wdir
        else:
            return ''
        
    def get_arguments(self):
        if self.args_enabled:
            return self.args
        else:
            return ''
        
    def get_python_arguments(self):
        if self.python_args_enabled:
            return self.python_args
        else:
            return ''
        
        
def _get_run_configurations():
    history_count = CONF.get('run', 'history', 20)
    return CONF.get('run', 'configurations', [])[:history_count]

def _set_run_configurations(configurations):
    history_count = CONF.get('run', 'history', 20)
    CONF.set('run', 'configurations', configurations[:history_count])
        
def get_run_configuration(fname):
    """Return script *fname* run configuration"""
    configurations = _get_run_configurations()
    for filename, options in configurations:
        if fname == filename:
            runconf = RunConfiguration()
            runconf.set(options)
            return runconf


class RunConfigOptions(QWidget):
    def __init__(self, parent=None):
        super(RunConfigOptions, self).__init__(parent)
        self.runconf = RunConfiguration()
        
        common_group = QGroupBox(self.tr("General settings"))
        common_layout = QGridLayout()
        common_group.setLayout(common_layout)
        self.clo_cb = QCheckBox(self.tr("Command line options:"))
        common_layout.addWidget(self.clo_cb, 0, 0)
        self.clo_edit = QLineEdit()
        self.connect(self.clo_cb, SIGNAL("toggled(bool)"),
                     self.clo_edit.setEnabled)
        self.clo_edit.setEnabled(False)
        common_layout.addWidget(self.clo_edit, 0, 1)
        self.wd_cb = QCheckBox(self.tr("Working directory:"))
        common_layout.addWidget(self.wd_cb, 1, 0)
        wd_layout = QHBoxLayout()
        self.wd_edit = QLineEdit()
        self.connect(self.wd_cb, SIGNAL("toggled(bool)"),
                     self.wd_edit.setEnabled)
        self.wd_edit.setEnabled(False)
        wd_layout.addWidget(self.wd_edit)
        browse_btn = QPushButton(get_std_icon('DirOpenIcon'), "", self)
        browse_btn.setToolTip(self.tr("Select directory"))
        self.connect(browse_btn, SIGNAL("clicked()"), self.select_directory)
        wd_layout.addWidget(browse_btn)
        common_layout.addLayout(wd_layout, 1, 1)
        self.debug_cb = QCheckBox(self.tr("Debug the script with pdb (Python "
                                          "debugger)"))
        common_layout.addWidget(self.debug_cb, 2, 0, 1, -1)
        
        radio_group = QGroupBox(self.tr("Interpreter"))
        radio_layout = QVBoxLayout()
        radio_group.setLayout(radio_layout)
        self.current_radio = QRadioButton(self.tr("Execute in current Python "
                                                  "or IPython interpreter"))
        radio_layout.addWidget(self.current_radio)
        self.new_radio = QRadioButton(self.tr("Execute in a new dedicated "
                                              "Python interpreter"))
        radio_layout.addWidget(self.new_radio)
        
        new_group = QGroupBox(self.tr("Dedicated Python interpreter"))
        self.connect(self.current_radio, SIGNAL("toggled(bool)"),
                     new_group.setDisabled)
        new_layout = QGridLayout()
        new_group.setLayout(new_layout)
        self.interact_cb = QCheckBox(self.tr("Interact with the Python "
                                             "interpreter after execution"))
        new_layout.addWidget(self.interact_cb, 0, 0, 1, -1)
        self.pclo_cb = QCheckBox(self.tr("Command line options:"))
        new_layout.addWidget(self.pclo_cb, 1, 0)
        self.pclo_edit = QLineEdit()
        self.connect(self.pclo_cb, SIGNAL("toggled(bool)"),
                     self.pclo_edit.setEnabled)
        self.pclo_edit.setEnabled(False)
        new_layout.addWidget(self.pclo_edit, 1, 1)
        pclo_label = QLabel(self.tr("Note: the <b>-u</b> option is "
                                    "automatically added to these commands"))
        pclo_label.setWordWrap(True)
        new_layout.addWidget(pclo_label, 2, 1)
        
        #TODO: Add option for "Post-mortem debugging"
        
        layout = QVBoxLayout()
        layout.addWidget(common_group)
        layout.addWidget(radio_group)
        layout.addWidget(new_group)
        self.setLayout(layout)

    def select_directory(self):
        """Select directory"""
        basedir = unicode(self.wd_edit.text())
        if not osp.isdir(basedir):
            basedir = os.getcwdu()
        directory = QFileDialog.getExistingDirectory(self,
                                        self.tr("Select directory"), basedir)
        if not directory.isEmpty():
            self.wd_edit.setText(directory)
            self.wd_cb.setChecked(True)
        
    def set(self, options):
        self.runconf.set(options)
        self.clo_cb.setChecked(self.runconf.args_enabled)
        self.clo_edit.setText(self.runconf.args)
        self.wd_cb.setChecked(self.runconf.wdir_enabled)
        self.wd_edit.setText(self.runconf.wdir)
        self.debug_cb.setChecked(self.runconf.debug)
        if self.runconf.current:
            self.current_radio.setChecked(True)
        else:
            self.new_radio.setChecked(True)
        self.interact_cb.setChecked(self.runconf.interact)
        self.pclo_cb.setChecked(self.runconf.python_args_enabled)
        self.pclo_edit.setText(self.runconf.python_args)
    
    def get(self):
        self.runconf.args_enabled = self.clo_cb.isChecked()
        self.runconf.args = unicode(self.clo_edit.text())
        self.runconf.wdir_enabled = self.wd_cb.isChecked()
        self.runconf.wdir = unicode(self.wd_edit.text())
        self.runconf.debug = self.debug_cb.isChecked()
        self.runconf.current = self.current_radio.isChecked()
        self.runconf.interact = self.interact_cb.isChecked()
        self.runconf.python_args_enabled = self.pclo_cb.isChecked()
        self.runconf.python_args = unicode(self.pclo_edit.text())
        return self.runconf.get()
    
    def is_valid(self):
        wdir = unicode(self.wd_edit.text())
        if not self.wd_cb.isChecked() or osp.isdir(wdir):
            return True
        else:
            QMessageBox.critical(self, self.tr("Run configuration"),
                                 self.tr("The following working directory is "
                                         "not valid:<br><b>%1</b>").arg(wdir))
            return False


class RunConfigOneDialog(QDialog):
    def __init__(self, parent=None):
        super(RunConfigOneDialog, self).__init__(parent)
        
        self.filename = None
        
        self.runconfigoptions = RunConfigOptions(self)
        self.runconfigoptions.set(RunConfiguration().get())
        
        bbox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.connect(bbox, SIGNAL("accepted()"), SLOT("accept()"))
        self.connect(bbox, SIGNAL("rejected()"), SLOT("reject()"))

        btnlayout = QHBoxLayout()
        btnlayout.addStretch(1)
        btnlayout.addWidget(bbox)
        
        layout = QVBoxLayout()
        layout.addWidget(self.runconfigoptions)
        layout.addLayout(btnlayout)
        self.setLayout(layout)

        self.setWindowIcon(get_icon("run.png"))
        
    def setup(self, fname):
        self.filename = fname
        self.setWindowTitle(self.tr("Run %1").arg(osp.basename(fname)))
            
    def accept(self):
        """Reimplement Qt method"""
        if not self.runconfigoptions.is_valid():
            return
        configurations = _get_run_configurations()
        configurations.insert(0, (self.filename, self.runconfigoptions.get()))
        _set_run_configurations(configurations)
        QDialog.accept(self)
    
    def get_configuration(self):
        return self.runconfigoptions.runconf


class RunConfigDialog(QDialog):
    def __init__(self, parent=None):
        super(RunConfigDialog, self).__init__(parent)
        
        combo_label = QLabel(self.tr("Select a run configuration:"))
        self.combo = QComboBox()
        self.combo.setMaxVisibleItems(20)
        self.combo.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLength)
        self.combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self.stack = QStackedWidget()

        bbox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.connect(bbox, SIGNAL("accepted()"), SLOT("accept()"))
        self.connect(bbox, SIGNAL("rejected()"), SLOT("reject()"))

        btnlayout = QHBoxLayout()
        btnlayout.addStretch(1)
        btnlayout.addWidget(bbox)
        
        layout = QVBoxLayout()
        layout.addWidget(combo_label)
        layout.addWidget(self.combo)
        layout.addSpacing(10)
        layout.addWidget(self.stack)
        layout.addLayout(btnlayout)
        self.setLayout(layout)

        self.setWindowTitle(self.tr("Run configurations"))
        self.setWindowIcon(get_icon("run.png"))
        
    def setup(self, fname):
        configurations = _get_run_configurations()
        for index, (filename, options) in enumerate(configurations):
            if fname == filename:
                break
        else:
            # There is no run configuration for script *fname*:
            # creating a temporary configuration that will be kept only if
            # dialog changes are accepted by the user
            configurations.insert(0, (fname, RunConfiguration().get()))
            index = 0
        for filename, options in configurations:
            widget = RunConfigOptions(self)
            widget.set(options)
            self.combo.addItem(filename)
            self.stack.addWidget(widget)
        self.connect(self.combo, SIGNAL("currentIndexChanged(int)"),
                     self.stack.setCurrentIndex)
        self.combo.setCurrentIndex(index)
        
    def accept(self):
        """Reimplement Qt method"""
        configurations = []
        for index in range(self.stack.count()):
            filename = unicode(self.combo.itemText(index))
            runconfigoptions = self.stack.widget(index)
            if not runconfigoptions.is_valid():
                return
            options = runconfigoptions.get()
            configurations.append( (filename, options) )
        _set_run_configurations(configurations)
        QDialog.accept(self)