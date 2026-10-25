#include <Arduino.h>
#include <ESP_I2S.h>
#include <math.h>

namespace {

constexpr uint32_t kSampleRate = 48000;
constexpr uint32_t kToneHz = 1000;
constexpr size_t kTableSize = kSampleRate / kToneHz;
constexpr float kAmplitude = 0.25f;

constexpr int kMclkPin = 7;
constexpr int kBclkPin = 4;
constexpr int kLrcPin = 5;
constexpr int kDataPin = 6;

I2SClass i2s;
int32_t sineTable[kTableSize];

int32_t makeSample(size_t index) {
  const float radians = 2.0f * PI * static_cast<float>(index) / static_cast<float>(kTableSize);
  const float normalized = sinf(radians) * kAmplitude;
  const int32_t sample24 = static_cast<int32_t>(normalized * 8388607.0f);
  return sample24 << 8;
}

}

void setup() {
  Serial.begin(115200);
  delay(300);

  Serial.println();
  Serial.println("CS4344 I2S DAC test");
  Serial.printf("Sample rate: %lu Hz\n", static_cast<unsigned long>(kSampleRate));
  Serial.printf("Tone: %lu Hz, stereo, 24-bit data in 32-bit slots\n", static_cast<unsigned long>(kToneHz));
  Serial.printf("MCLK=GPIO%d BCLK=GPIO%d LRC=GPIO%d DIN=GPIO%d\n", kMclkPin, kBclkPin, kLrcPin, kDataPin);

  for (size_t i = 0; i < kTableSize; ++i) {
    sineTable[i] = makeSample(i);
  }

  i2s.setPins(kBclkPin, kLrcPin, kDataPin, -1, kMclkPin);

  if (!i2s.begin(I2S_MODE_STD, kSampleRate, I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_STEREO)) {
    Serial.printf("I2S init failed, error %d\n", i2s.lastError());
    while (true) {
      delay(1000);
    }
  }

  Serial.println("I2S running");
}

void loop() {
  static size_t index = 0;
  const int32_t frame[2] = {sineTable[index], sineTable[index]};
  i2s.write(frame, sizeof(frame));
  index = (index + 1) % kTableSize;
}
