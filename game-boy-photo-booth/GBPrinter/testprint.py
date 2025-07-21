from GBPrinter import GBPrinter

with GBPrinter("/dev/ttyACM0", 115200) as gbp:
    gbp.printImageFromFile("testprint.png", 0.5)
