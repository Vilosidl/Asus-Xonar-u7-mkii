# 🎧 USB Audio Output Toggle Daemon

This project is a **background daemon** for Linux that allows you to **toggle audio output between headphones and speakers** on an **ASUS Xonar U7 MKII** USB sound card. It uses low-level USB communication, `pactl` for volume control, and local socket communication for triggering.

---

## 📦 Features

- Detects and interacts with the ASUS Xonar U7 MKII USB device  
- Switches audio output mode by modifying a USB data payload  
- Reads and sets volume using `pactl`  
- Sends desktop notifications using `notify-send`  
- Listens for control commands via a TCP socket (localhost)

---

## 🖥️ Requirements

Make sure the following dependencies are installed:

- Python 3.x
- `pyusb`
- `pactl` (from PulseAudio or PipeWire)
- `notify-send` (usually from the `libnotify-bin` package)

Install `pyusb`:

```bash
pip install pyusb
```

---

## 📁 Project Structure

- `main.py` — the main daemon that handles USB control and socket commands  
- `data` — a file storing the current USB payload state  
- `client.py` — a small script that sends a toggle command to the daemon

---

## 🚀 How to Use

### 1. Create a `data` file

```bash
echo "array('B', [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 48])" > data
```

(48 at index 10 = "headphones", 160 = "speakers")

---

### 2. Add udev rules (non-root USB access)

To access the ASUS Xonar U7 MKII without root privileges, create a `udev` rule:

```bash
sudo nano /etc/udev/rules.d/99-usb.rules
```

Paste the following:

```bash
# ASUS Xonar U7 MKII — allow user access
SUBSYSTEM=="usb", ATTR{idVendor}=="0b05", ATTR{idProduct}=="183c", MODE="0666", GROUP="audio"
```

Then reload rules and trigger:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Unplug and reconnect the USB device.

To verify:

```bash
lsusb
```

Look for:

```
Bus XXX Device YYY: ID 0b05:183c ASUSTek Computer, Inc. Xonar U7 MKII
```

---

### 3. Start the daemon

```bash
python3 main.py
```

The daemon will listen on `127.0.0.1:65432`.

---

### 4. Toggle output from client

```bash
python3 client.py
```

Sends the `"change"` command to toggle between headphones and speakers.

---

## ⚠️ Notes

- The sound card must be **connected via USB**
- The **kernel driver must be detached** from USB interface 4 (the daemon handles this)
- Make sure the sink name in `set_volume()` matches your system:

```python
sink = "alsa_output.usb-ASUS_Xonar_U7_MKII-00.analog-stereo"
```

List your available sinks:

```bash
pactl list short sinks
```

---

## 📜 Example Output

```
Daemon listening on 127.0.0.1:65432
Connected by ('127.0.0.1', 54321)
Received command: change
```

---

## 💡 Future Improvements

- Add DBus or HTTP interface
- Config file for sink name and port
- Multi-device or multi-profile support

---

## 📄 License

This project is licensed under the MIT License.
