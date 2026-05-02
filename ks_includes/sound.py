import logging
import shlex
import subprocess


class SoundManager:
    def __init__(self, config):
        self.enabled = config.getboolean("main", "sounds_enable", fallback=False)
        self.command_template = config.get("main", "sounds_command", fallback="")
        self.serial_device = config.get("main", "sounds_serial_device", fallback="")
        self.serial_encoding = config.get("main", "sounds_serial_encoding", fallback="ascii")

    def play(self, keyword):
        if not self.enabled or not keyword:
            return
        keyword = keyword.strip().lower()
        if self.command_template:
            self._run_command(keyword)
        if self.serial_device:
            self._write_serial(keyword)

    def _run_command(self, keyword):
        try:
            command = self.command_template.format(keyword=keyword)
            subprocess.Popen(shlex.split(command), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logging.debug("sound command sent: %s", command)
        except Exception as e:
            logging.error("Failed to run sound command for '%s': %s", keyword, e)

    def _write_serial(self, keyword):
        line = f"sound {keyword}\n"
        try:
            with open(self.serial_device, "wb", buffering=0) as serial_port:
                serial_port.write(line.encode(self.serial_encoding, errors="ignore"))
            logging.debug("sound serial sent: %s -> %s", line.strip(), self.serial_device)
        except Exception as e:
            logging.error("Failed to write sound command '%s' to %s: %s", keyword, self.serial_device, e)
