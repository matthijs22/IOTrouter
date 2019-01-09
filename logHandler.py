class LogHandler:

    def __init__(self, logfile):
        self._file = open(logfile, "w")

    def createEntry(self, message):
        self._file.write(message + "\n")
        self._file.flush()
