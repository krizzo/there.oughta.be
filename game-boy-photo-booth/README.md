# there.oughta.be/a/game-boy-photo-booth

This project was presented at https://there.oughta.be/a/game-boy-photo-booth. Check out the blog article or the video below for an overview.

This project is another variant of a photo booth for another one of my cousin who got married. This time it uses a Game Boy Camera to record a video simultaneously with a regular camera and offers guests to print out stills from their recording on a Game Boy Camera.

[![Youtube Video: WiFi Game Boy Cartridge](https://img.youtube.com/vi/9KqTbu14pp0/0.jpg)](https://youtu.be/9KqTbu14pp0)

This folder contains the code for different aspects of this project, but since this project and the code are very specific to the exact hardware (camera brands, micro controller etc., see https://there.oughta.be/a/game-boy-photo-booth) I used, it is unlikely that you will be able to use the code as is. You will probably have to make several adjustments for your needs or pick the parts you want to reuse.

<a href="https://www.buymeacoffee.com/there.oughta.be" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-blue.png" alt="Buy Me A Coffee" height="47" width="174" ></a>


## photobooth-py

This is the main Python script of the photo booth, controlling all the peripherals and serving the web-based GUI. Note, that this code has been derived from the older [bullet time video booth](https://github.com/Staacks/there.oughta.be/tree/master/bullet-time-video-booth) and some of it structure is unnecessarily complicated as parts have been stripped that are no longer required for the Game Boy Photo Booth (like the error state recovery which originally reset the entire USB bus).


## GBPrinter

The Python module to send tile data to a printer. Check `testprint.py` for an example on how to use it in order to print an arbitrary image file. This is meant to be used with a micro controller running the code from the Pro Micro folder.

Note that `printImageFromFile` takes two parameters: The first is the image file to print, the second is "exposure", which is an adjustment to how much the thermal paper is heated, i.e. it adjusts overall brightness of the printout.

Keep in mind that the Game Boy Printer can only print rows of Game Boy tiles, which means that it always prints 8 lines of pixels at the same time. Therefore, **the image has to have a height that is a multiple of 8 after it has been scaled to a width of 160 pixels**.


## pro_micro

This folder contains the subfolder `gblink` which is an Arduino project to hook up the Pro Micro's SPI interface to a USB serial interface. This code is rather minimalistic and should run on most Arduino-compatible micro controllers with little or no modification. Make sure to use a micro controller with 5V logic level or level shifters.

Simply cut a cheap link cable in half and solder it to the Pro Micro (or the SPI pins of a similar microcontroller) as follows:

![Pro micro connections](pro_micro/pinout.jpg?raw=true "Connecting the Pro Micro to a link cable plug for the Game Boy Printer")

You can use `test.py` to test the connection by checking if you receive the default answer from the Game Boy Printer.


## bleButton

The code for the big push buttons that control the photo booth are in their own repository at [Staacks/pico-w-ble-button](https://github.com/Staacks/pico-w-ble-button) in order to avoid confusion about the license. They are based on a Raspberry Pi Pico W and act as a BLE HID keyboard.

