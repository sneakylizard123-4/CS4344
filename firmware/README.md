# CS4344 test firmware

This is host-side example firmware for the CS4344 board. The PCB has no
microcontroller, oscillator, or configuration bus. The firmware runs on an
ESP32-S3 development board and supplies the I2S clocks and data that the DAC
needs.

`SPDX-License-Identifier: MIT`

## What it does

The example outputs a 1 kHz stereo sine wave at 48 kHz. The DAC receives:

- MCLK at 12.288 MHz (256 x 48 kHz)
- BCLK at 3.072 MHz (64 x 48 kHz)
- LRCK at 48 kHz
- 24-bit samples, left-aligned in 32-bit I2S slots

The 32-bit slot width is intentional. The Arduino ESP_I2S wrapper fixes the
MCLK multiple at 256, and the ESP-IDF clock setup rejects a 24-bit slot width
with that multiple. A 32-bit slot keeps the required 64 x Fs bit clock, and the
CS4344 reads the first 24 bits of each slot.

## Hardware

Target: ESP32-S3-DevKitC-1, 8 MB flash, no PSRAM.

| CS4344 board | J2 pin | ESP32-S3 pin |
|---|---|---|
| +3.3 V | 1 | 3V3 |
| SD | 2 | GPIO6 |
| SCK | 3 | GPIO4 |
| FS | 4 | GPIO5 |
| MCLK | 5 | GPIO7 |
| GND | 6 | GND |

Connect the grounds together. Keep the clock and data wires short, especially
MCLK and BCLK. The board runs from 3.3 V only. Do not connect it to 5 V.

These pins are defaults in `src/main.cpp`. Change them if your dev board uses
different pins, but avoid the ESP32-S3 strapping pins and the USB pins.

## Build and flash

PlatformIO is required. The project was built with PlatformIO Core 6.1.19 and
the `espressif32@8.0.0` platform.

```sh
cd firmware
pio run
pio run -t upload
pio device monitor
```

The monitor runs at 115200 baud and prints the pin map and a startup message.
If I2S initialization fails, the firmware prints the error code and stops.

## Test

1. Connect the board and dev kit as shown above.
2. Flash the firmware and open the serial monitor.
3. Connect the 3.5 mm jack to an amplifier or powered speakers.
4. Turn the amplifier volume down before powering up.
5. You should hear a steady 1 kHz tone in both channels.

The output is line level. It will not drive headphones directly.

This firmware compiles, but it has not been run on a fabricated CS4344 board
yet. The PCB and enclosure are still untested.

## License

The firmware is licensed under the MIT License. See
[LICENSE-MIT](../LICENSE-MIT).
