import minimalmodbus
import time
from globals import ParseConfig

class N4dba06Controller:
    def __init__(self, serial_port):
        self.instrument = minimalmodbus.Instrument(serial_port, 1)
        self.instrument.serial.baudrate = 19200
        self.instrument.serial.timeout = 3
        self.port_mapping = self._load_addresses()

    def _load_addresses(self):
        in_ports = ParseConfig('Ports', 'in_ports', True)
        out_ports = ParseConfig('Ports', 'out_ports', True)

        port_mapping = {
            'in_ports': {},
            'out_ports': {}
        }

        for port in in_ports:
            value = ParseConfig('port_mapping', port)
            if value is not None:
                port_mapping['in_ports'][port] = int(value, 0)

        for port in out_ports:
            value = ParseConfig('port_mapping', port)
            if value is not None:
                port_mapping['out_ports'][port] = int(value, 0)

        return port_mapping

    def read_port(self, port):
        if port not in self.port_mapping['in_ports']:
            raise ValueError("Invalid port name.")

        start_time = time.perf_counter()
        while True:
            try:
                value = self.instrument.read_register(self.port_mapping['in_ports'][port], functioncode=3)
                break
            except minimalmodbus.NoResponseError:
                time.sleep(0.1)
        print(f"read_time: {time.perf_counter() - start_time}")

        if port in ['Vi1', 'Vi2', 'Ii']:
            value *= 0.01

        return value

    def write_port(self, port, value):
        if port not in self.port_mapping['out_ports']:
            raise ValueError("Invalid port name.")

        if port in ['Vo1', 'Vo2']:
            value *= 100

        start_time = time.perf_counter()
        while True:
            try:
                self.instrument.write_register(self.port_mapping['out_ports'][port], value, functioncode=6)
                break
            except minimalmodbus.NoResponseError:
                time.sleep(0.1)
        print(f"write_time: {time.perf_counter() - start_time}")

# Usage example:
#serial_port = ParseConfig('serial', 'port')
#controller = N4dba06Controller(serial_port)
#value = controller.read_port('Vi1')
#print(value)
#controller.write_port('Vo2', 100)