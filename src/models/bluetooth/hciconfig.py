from src.models import Executor


class HciConfig(Executor):
    """hciconfig - HCI device configuration utility

    Usage:
        hciconfig
        hciconfig [-a] hciX [command ...]

    Commands:
        up                     : Open and initialize HCI device
        down                   : Close HCI device
        reset                  : Reset HCI device
        rstat                  : Reset statistic counters
        auth                   : Enable Authentication
        noauth                 : Disable Authentication
        encrypt                : Enable Encryption
        noencrypt              : Disable Encryption
        piscan                 : Enable Page and Inquiry scan
        noscan                 : Disable scan
        iscan                  : Enable Inquiry scan
        pscan                  : Enable Page scan
        ptype      [type]      : Get/Set default packet type
        lm         [mode]      : Get/Set default link mode
        lp         [policy]    : Get/Set default link policy
        name       [name]      : Get/Set local name
        class      [class]     : Get/Set class of device
        voice      [voice]     : Get/Set voice setting
        iac        [iac]       : Get/Set inquiry access code
        inqtpl     [level]     : Get/Set inquiry transmit power level
        inqmode    [mode]      : Get/Set inquiry mode
        inqdata    [data]      : Get/Set inquiry data
        inqtype    [type]      : Get/Set inquiry scan type
        inqparms   [win]       : Get/Set inquiry scan window and interval
        pageparms  [win]       : Get/Set page scan window and interval
        pageto     [to]        : Get/Set page timeout
        afhmode    [mode]      : Get/Set AFH mode
        sspmode    [mode]      : Get/Set Simple Pairing Mode
        aclmtu     <mtu>       : Set ACL MTU and number of packets
        scomtu     <mtu>       : Set SCO MTU and number of packets
        delkey     <bdaddr>    : Delete link key from the device
        oobdata                : Get local OOB data
        commands               : Display supported commands
        features               : Display device features
        version                : Display version information
        revision               : Display revision information
        block      <bdaddr>    : Add a device to the reject list
        unblock    <bdaddr>    : Remove a device from the reject list
        lerandaddr <bdaddr>    : Set LE Random Address
        leadv      [type]      : Enable LE advertising
                        0 - Connectable undirected advertising (default)
                        3 - Non connectable undirected advertising
        noleadv                : Disable LE advertising
        lestates               : Display the supported LE states
    """
    command = "hciconfig"
    requires_tempfile = False
    requires_tempdir = False
    requires_root = False

    def __init__(self):
        super().__init__()
        self.dirty = False

    async def run(self, *args, **kwargs):
        print(args)
        return await super().run(*args, **kwargs)

    async def get_result(self):
        if self.proc:
            return await self.proc.wait()

    async def __aenter__(self):
        self._interface_data = await self.interfaces
        return self

    async def __aexit__(self):
        self._interface_data = None

    @property
    async def interfaces(self):
        if not self.dirty:
            await self.run()
            self.dirty = True
        data = await self.readlines()
        return data


# class Interface:
#     def __init__(self, interface_data):
#         first_row = interface_data[0].decode().split(':')
#         name, itype, bus = first_row[0], first_row[]
