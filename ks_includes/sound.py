import glob
import logging
import shlex
import subprocess


class SoundManager:
    def __init__(self, config):
        self.config = config
        self.reload_config()

    def reload_config(self, *_args):
        self.enabled = self.config.getboolean("main", "sounds_enable", fallback=False)
        self.output = self.config.get("main", "sounds_output", fallback="both")
        self.muted = self.config.getboolean("main", "sounds_mute", fallback=False)
        self.volume = max(0, min(100, self.config.getint("main", "sounds_volume", fallback=100)))
        self.command_template = self.config.get("main", "sounds_command", fallback="")
        self.serial_enabled = self.config.getboolean("main", "sounds_serial_enable", fallback=False)
        self.serial_device = self.config.get("main", "sounds_serial_device", fallback="")
        self.serial_encoding = self.config.get("main", "sounds_serial_encoding", fallback="ascii")

    @staticmethod
    def discover_serial_devices():
        patterns = ("/dev/ttyUSB*", "/dev/ttyACM*", "/dev/serial/by-id/*")
        devices = []
        for pattern in patterns:
            devices.extend(glob.glob(pattern))
        return sorted(set(devices))

    def play(self, keyword):
        if not self.enabled or self.muted or not keyword:
            return
        keyword = keyword.strip().lower()
        if self.output in ("audio", "both") and self.command_template:
            self._run_command(keyword)
        if self.output in ("serial", "both") and self.serial_enabled and self.serial_device:
            self._write_serial(f"sound {keyword}\n")

    def set_volume(self, value):
        self.volume = max(0, min(100, int(value)))
        if self.output in ("serial", "both") and self.serial_enabled and self.serial_device:
            self._write_serial(f"volume {self.volume}\n")

    def _run_command(self, keyword):
        try:
            command = self.command_template.format(keyword=keyword, volume=self.volume)
            subprocess.Popen(shlex.split(command), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            logging.error("Failed to run sound command for '%s': %s", keyword, e)

    def _write_serial(self, line):
        try:
            with open(self.serial_device, "wb", buffering=0) as serial_port:
                serial_port.write(line.encode(self.serial_encoding, errors="ignore"))
        except Exception as e:
            logging.error("Failed to write '%s' to %s: %s", line.strip(), self.serial_device, e)
