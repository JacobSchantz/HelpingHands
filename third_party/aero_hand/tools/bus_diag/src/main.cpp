// Aero Hand Open control board: read-only bus diagnostic (no servo writes, no motion).
// Board nets (from hardware/PCB/Aero_hand_open_right .kicad_pcb):
//   XIAO pad 2 = GPIO2/D1 <- U2 (LVC1G125) Y   = ESP RX from bus, R5 10k pull-up to 3V3
//   XIAO pad 3 = GPIO3/D2 -> U1 (LVC1G126) A   = ESP TX to bus, R4 10k pull-up, R6 1k to Q1 base (auto-direction)
//   XIAO pad 12 = 3V3 (powers U1/U2/pull-ups), pad 13 = GND. Servo V+ comes from XT30 6 V only.
#include <Arduino.h>

static const int PIN_RX = 2, PIN_TX = 3;
static const uint32_t BAUDS[] = {1000000, 500000, 250000, 128000, 115200, 76800, 57600, 38400};

static void pinTests() {
  Serial2.end();
  pinMode(PIN_RX, INPUT_PULLDOWN); pinMode(PIN_TX, INPUT_PULLDOWN); delay(5);
  int rx = digitalRead(PIN_RX), tx = digitalRead(PIN_TX);
  int rxmv = analogReadMilliVolts(PIN_RX), txmv = analogReadMilliVolts(PIN_TX);
  pinMode(PIN_RX, INPUT_PULLDOWN); pinMode(PIN_TX, INPUT_PULLDOWN); delay(2);
  Serial.printf("PINTEST GPIO2(pad2,RX) w/ internal pulldown: %s (%d mV)  [HIGH = joint + R5 pull-up + 3V3 OK]\n", rx ? "HIGH" : "LOW", rxmv);
  Serial.printf("PINTEST GPIO3(pad3,TX) w/ internal pulldown: %s (%d mV)  [HIGH = joint + R4/Q1 + 3V3 OK]\n", tx ? "HIGH" : "LOW", txmv);
  // TX idle high -> Q1 off -> RXEN low -> U2 enabled: GPIO2 now mirrors the bus line itself.
  pinMode(PIN_TX, OUTPUT); digitalWrite(PIN_TX, HIGH); delay(5);
  int bus = digitalRead(PIN_RX);
  int busmv = analogReadMilliVolts(PIN_RX);
  Serial.printf("PINTEST bus idle via U2 (TX high): %s (%d mV)  [LOW = something holds the bus low, e.g. unpowered servo or short]\n", bus ? "HIGH" : "LOW", busmv);
  // GPIO2 with internal PULL-UP while U2 is enabled: an open pad-2 joint reads HIGH (internal pull-up);
  // a connected pad with U2 driving a low bus reads LOW.
  pinMode(PIN_RX, INPUT_PULLUP); delay(5);
  Serial.printf("PINTEST GPIO2 internal pull-up, U2 enabled (TX high): %s\n", digitalRead(PIN_RX) ? "HIGH" : "LOW");
  // TX low -> Q1 on -> RXEN high -> U2 tri-stated, so GPIO2 sees only R5 10k pull-up.
  // With internal PULL-DOWN: connected pad -> HIGH (10k beats ~45k); open pad -> LOW.
  pinMode(PIN_RX, INPUT_PULLDOWN); digitalWrite(PIN_TX, LOW); delay(5);
  int rxDisabled = digitalRead(PIN_RX);
  digitalWrite(PIN_TX, HIGH); delay(5);
  int rxEnabled = digitalRead(PIN_RX);
  Serial.printf("PINTEST GPIO2 pulldown: TX low (U2 off, R5 only) = %s | TX high (U2 on, bus) = %s  [HIGH then LOW = pad 2 good, bus held low]\n",
                rxDisabled ? "HIGH" : "LOW", rxEnabled ? "HIGH" : "LOW");
  pinMode(PIN_TX, INPUT);
}

static int txrx(uint8_t id, uint8_t inst, const uint8_t* p, uint8_t n, uint8_t* out, int outMax, uint32_t baud) {
  uint8_t pkt[32]; uint8_t len = n + 2; int k = 0;
  pkt[k++] = 0xFF; pkt[k++] = 0xFF; pkt[k++] = id; pkt[k++] = len; pkt[k++] = inst;
  uint8_t sum = id + len + inst;
  for (int i = 0; i < n; i++) { pkt[k++] = p[i]; sum += p[i]; }
  pkt[k++] = ~sum;
  while (Serial2.available()) Serial2.read();
  Serial2.write(pkt, k); Serial2.flush();
  uint32_t t0 = millis(); int got = 0;
  uint32_t tmo = 8 + (uint32_t)(20000000ULL / baud) / 1000 * 4;
  while (millis() - t0 < tmo && got < outMax) { if (Serial2.available()) out[got++] = Serial2.read(); }
  return got;
}

// Parse a status packet; returns param count or -1.
static int parse(const uint8_t* b, int n, uint8_t* id, uint8_t* err, const uint8_t** params) {
  for (int i = 0; i + 5 < n; i++) {
    if (b[i] == 0xFF && b[i + 1] == 0xFF && b[i + 2] != 0xFF) {
      uint8_t len = b[i + 3]; if (i + 3 + len >= n) return -2;
      uint8_t sum = 0; for (int j = 2; j < 4 + len - 1; j++) sum += b[i + j];
      if ((uint8_t)~sum != b[i + 3 + len]) return -3;
      *id = b[i + 2]; *err = b[i + 4]; *params = &b[i + 5]; return len - 2;
    }
  }
  return -1;
}

static void hexdump(const char* tag, const uint8_t* b, int n) {
  Serial.printf("%s (%d bytes):", tag, n); for (int i = 0; i < n; i++) Serial.printf(" %02X", b[i]); Serial.println();
}

static int foundId = -1; static uint32_t foundBaud = 0;

static void scan() {
  uint8_t buf[96]; uint8_t id, err; const uint8_t* p;
  for (uint32_t baud : BAUDS) {
    Serial2.begin(baud, SERIAL_8N1, PIN_RX, PIN_TX); delay(5);
    int n = txrx(0xFE, 0x01, nullptr, 0, buf, sizeof buf, baud);
    int r = parse(buf, n, &id, &err, &p);
    if (n) hexdump("  raw", buf, n);
    Serial.printf("SCAN baud %7lu broadcast ping: %s", (unsigned long)baud, r >= 0 ? "REPLY" : (n ? "garbage" : "silent"));
    if (r >= 0) Serial.printf(" id=%u err=0x%02X", id, err);
    Serial.println();
    if (r >= 0 && foundId < 0) { foundId = id; foundBaud = baud; }
  }
  {  // always list every ID on the bus
    Serial2.begin(1000000, SERIAL_8N1, PIN_RX, PIN_TX); delay(5);
    int hits = 0;
    for (int i = 0; i <= 253; i++) {
      int n = txrx(i, 0x01, nullptr, 0, buf, sizeof buf, 1000000);
      if (parse(buf, n, &id, &err, &p) >= 0) { Serial.printf("SCAN 1M id %d answered\n", i); hits++; if (foundId < 0) { foundId = i; foundBaud = 1000000; } }
    }
    Serial.printf("SCAN 1M per-ID ping 0..253: %d servo(s) answered\n", hits);
  }
}

static void readRegs(bool full) {
  if (foundId < 0) return;
  Serial2.begin(foundBaud, SERIAL_8N1, PIN_RX, PIN_TX); delay(2);
  uint8_t buf[96]; uint8_t id, err; const uint8_t* p;
  if (full) {
    uint8_t q[2] = {0, 40};
    int n = txrx(foundId, 0x02, q, 2, buf, sizeof buf, foundBaud);
    int r = parse(buf, n, &id, &err, &p);
    if (r >= 40) {
      Serial.printf("EEPROM id=%u err=0x%02X fw=%u.%u model=%u ID=%u baudIdx=%u minV=%.1fV maxV=%.1fV maxTemp=%uC prot.current(28)=%u mode=%u\n",
        id, err, p[0], p[1], p[3] | (p[4] << 8), p[5], p[6], p[15] / 10.0, p[14] / 10.0, p[13], p[28] | (p[29] << 8), p[33]);
      hexdump("EEPROM 0..39", p, r);
    } else Serial.printf("EEPROM read failed (%d)\n", r);
  }
  uint8_t q[2] = {56, 15};
  int n = txrx(foundId, 0x02, q, 2, buf, sizeof buf, foundBaud);
  int r = parse(buf, n, &id, &err, &p);
  if (r >= 15) {
    int16_t cur = (p[13] | ((p[14] & 0x7F) << 8)) * ((p[14] & 0x80) ? -1 : 1);
    Serial.printf("TELEM id=%u err=0x%02X pos=%u voltage=%.1fV temp=%uC moving=%u current=%d (raw)\n",
      id, err, (p[0] | (p[1] << 8)) & 0x7FFF, p[6] / 10.0, p[7], p[10], cur);
  } else Serial.printf("TELEM read failed (%d, %d bytes)\n", r, n);
}

void setup() {
  Serial.begin(921600);
  delay(1500);
  Serial.println("\n=== AERO BUS DIAG (read-only) ===");
}

void loop() {
  static int round = 0;
  Serial.printf("--- round %d ---\n", round);
  pinTests();
  if (round == 0 || foundId < 0) scan();
  readRegs(round == 0 || round % 10 == 0);
  round++;
  delay(1000);
}
