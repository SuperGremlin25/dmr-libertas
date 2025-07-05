# DMR Libertas Hardware Setup Guide

## Overview

This document provides detailed instructions for setting up the hardware components of the DMR Libertas system. Proper hardware configuration is essential for optimal performance and reliability.

## Required Components

### Base Station

- Raspberry Pi 4B (4GB or 8GB RAM recommended)
- MMDVM (Multi-Mode Digital Voice Modem) HAT
- Cooling case with fan
- 32GB+ microSD card (industrial grade recommended)
- 5V 3A power supply with USB-C connector
- Ethernet cable or Wi-Fi adapter

### Radio Interface

- MMDVM hotspot board (supports DMR, D-Star, YSF, P25, NXDN)
- SMA antenna connector
- Dual-band antenna (VHF/UHF)
- Optional: RF amplifier for extended range

### Optional Components

- GPS module for time synchronization
- OLED display for status information
- Battery backup system (UPS)
- External band-pass filters for noisy RF environments

## Assembly Instructions

### 1. Prepare the Raspberry Pi

1. Install the Raspberry Pi in the cooling case
2. Connect the MMDVM HAT to the GPIO pins on the Raspberry Pi
3. Secure the HAT with the provided standoffs and screws
4. Insert the microSD card into the Raspberry Pi

### 2. Connect the Radio Components

1. Attach the antenna to the SMA connector on the MMDVM board
2. If using an external amplifier:
   - Connect the MMDVM output to the amplifier input
   - Connect the amplifier output to the antenna
   - Ensure proper grounding of all components

### 3. Power and Network Setup

1. Connect the Ethernet cable to your network (recommended for reliability)
2. Alternatively, configure Wi-Fi in the software setup phase
3. Connect the power supply to the Raspberry Pi
4. Verify the power LED illuminates on both the Pi and MMDVM board

## Hardware Configuration

### MMDVM Jumper Settings

| Jumper | Position | Function |
|--------|----------|----------|
| JP1    | Closed   | Enable UART |
| JP2    | Open     | Disable PTT inversion |
| JP3    | Closed   | Enable 3.3V logic level |

### DIP Switch Configuration

| Switch | Position | Function |
|--------|----------|----------|
| SW1    | ON       | Enable DMR mode |
| SW2    | OFF      | Disable D-STAR mode |
| SW3    | OFF      | Disable YSF mode |
| SW4    | OFF      | Disable P25 mode |

## Testing the Hardware

### Power-On Test

1. Apply power to the system
2. Verify the following LEDs illuminate:
   - Raspberry Pi power LED (red)
   - MMDVM status LED (green)
   - Network activity LED (flashing amber when connected)

### RF Test

1. Use an SWR meter to verify antenna performance
2. Target SWR should be less than 1.5:1 for optimal performance
3. Verify transmit power output with a power meter (if available)

## Troubleshooting

### No Power

- Verify power supply output with multimeter (should be 5V ±0.25V)
- Check USB cable for damage
- Try an alternative power supply

### No RF Output

- Verify MMDVM jumper settings
- Check antenna connection
- Verify software is configured for transmit
- Check GPIO pin configuration in software

### Overheating

- Verify cooling fan operation
- Ensure adequate ventilation around the case
- Consider adding additional cooling if operating in high-temperature environments

## Environmental Considerations

- Operating temperature: 0°C to 50°C (32°F to 122°F)
- Humidity: 10% to 90% non-condensing
- Protect from direct sunlight and moisture
- Ensure adequate ventilation

## Next Steps

After completing the hardware setup:

1. Proceed to the software installation guide
2. Configure the network settings
3. Set up the DMR parameters
4. Perform a full system test

## Reference Diagrams

```
+---------------+        +---------------+
|               |        |               |
| Raspberry Pi  |<------>| MMDVM HAT     |
|               |  GPIO  |               |
+---------------+        +-------+-------+
                                 |
                                 | RF
                                 |
                         +-------v-------+
                         |               |
                         | Antenna       |
                         |               |
                         +---------------+
```

---

*Last updated: July 2025*