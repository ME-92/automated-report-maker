
import logging

from PyQt5 import QtCore


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

text_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
text_format_2 = logging.Formatter('%(levelname)s - %(message)s')
text_format_3 = logging.Formatter('► %(message)s')

file_handler = logging.FileHandler('./logger/log.txt')
file_handler.setFormatter(text_format)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(text_format_2)

log.addHandler(file_handler)
log.addHandler(stream_handler)


class UiHandler(logging.Handler, QtCore.QObject):
    signal = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        QtCore.QObject.__init__(self)
        logging.Handler.__init__(self)
        self.parent = parent

        self.setFormatter(text_format_3)
        self.setLevel(logging.INFO)
        self.signal.connect(self.parent.appendPlainText)

    def emit(self, record):
        msg = self.format(record)
        self.signal.emit(msg)
