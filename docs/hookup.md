# HOWTO Hookup Development Boards

## Connectors

[More information here](http://infocenter.arm.com/help/topic/com.arm.doc.faqs/attached/13634/cortex_debug_connectors.pdf)

The JTAG/SWD connectors to Cortex-M boards are generally of two forms.

 * 0.1" header pins in vendor specific order.
 * A Cortex Debug connector. This is a 10 (2x5) pin connector with 0.05" pin spacing.

The JTAG/SWD dongles generally have a 20 (2x10) pin 0.1" connector that follows the older ARM JTAG/SWD standard.
You need to adapt between the two - it's a re-wiring job.

 * [20 to 10 pin adapter](https://www.adafruit.com/products/2094)
 * [10 pin cable](https://www.adafruit.com/products/1675)


## ST Development Boards

![mb1035b_image](https://github.com/deadsy/pycs/blob/master/docs/pics/mb1035b.jpg "mb1035b_image")

The ST boards have a 6 pin SWD debug connector.
The JLINK has a 20 pin connector.

 * Board Pin 1 (VDD_TARGET) - No Connect (this is not actually a target reference voltage)
 * Board Pin 2 (SWCLK) - JLINK Pin 9 (SWCLK)
 * Board Pin 3 (GND) - JLINK Pin 4 (GND)
 * Board Pin 4 (SWDIO) - JLINK Pin 7 (SWDIO)
 * Board Pin 5 (NRST) - JLINK Pin 15 (RESET)
 * Board Pin 6 (SWO) - JLINK Pin 13 (SWO) - this is optional
 * Board 3V Vdd - JLINK Pin 1 (VTref)

Leave the ST-Link/Discovery jumpers installed so the debug signals are passed to the Discovery CPU.
