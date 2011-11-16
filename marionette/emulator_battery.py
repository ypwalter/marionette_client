class EmulatorBattery(object):

    def __init__(self, emulator):
        self.emulator = emulator

    def get_state(self):
        status = {}
        state = {}

        response = self.emulator._run_telnet('power display')
        for line in response:
            if ':' in line:
                field, value = line.split(':')
                value = value.strip()
                if value == 'true':
                    value = True
                elif value == 'false':
                    value = False
                elif field == 'capacity':
                    value = float(value)
                status[field] = value

        state['level'] = status.get('capacity', 0.0) / 100
        if status.get('status') == 'Charging':
            state['charging'] = True
        else:
            state['charging'] = False

        return state
