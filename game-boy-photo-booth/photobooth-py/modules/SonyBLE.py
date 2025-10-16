import asyncio
from bleak import BleakClient, BleakGATTCharacteristic
from threading import Thread
import subprocess

class SonyBLE:

    def __init__(self, address):
        self.bleCamAddress = address
        self.loop = asyncio.new_event_loop()

    bleCmdUUID = "0000ff01-0000-1000-8000-00805f9b34fb"
    bleStatusUUId = "0000ff02-0000-1000-8000-00805f9b34fb"

    recordRequest = asyncio.Event()

    bleRecordPayload1 = bytearray([0x01,0x0f])
    bleRecordPayload2 = bytearray([0x01,0x0e])
    bleStatusRecStart = bytearray([0x02,0xd5, 0x20])
    bleStatusRecStop = bytearray([0x02,0xd5, 0x00])

    camStatusRecording = False
    running = False

    async def mainBLE(self, address):
        print("BLE starting...")
        async with BleakClient(address) as client:
            print("BLE connected.")
            await client.start_notify(self.bleStatusUUId, self.status_notification_handler)
            print("BLE subscribed to status notifications")
            while self.running:
                print("BLE ready.")
                await self.recordRequest.wait()
                if self.running:
                    print("BLE triggering...")
                    await client.write_gatt_char(self.bleCmdUUID, self.bleRecordPayload1)
                    await asyncio.sleep(0.1)
                    await client.write_gatt_char(self.bleCmdUUID, self.bleRecordPayload2)
                    self.recordRequest.clear()
            await client.stop_notify(self.bleStatusUUId)
            await client.disconnect()
            self.recordRequest.clear()
            print("BLE disconnected.")

    def status_notification_handler(self, characteristic: BleakGATTCharacteristic, data: bytearray):
        if data == self.bleStatusRecStart:
            self.camStatusRecording = True
            print("BLE recording started")
        elif data == self.bleStatusRecStop:
            self.camStatusRecording = False
            print("BLE recording stopped")

    def triggerRecording(self):
        self.loop.call_soon_threadsafe(self.recordRequest.set)

    def isRecording(self):
        return self.camStatusRecording

    def isRunning(self):
        return self.running

    def connect(self):
        self.running = True

        #System call to disconnect camera if it is already connected.
        try:
            subprocess.call(['bluetoothctl','disconnect',self.bleCamAddress],timeout=2)
        except (subprocess.CalledProcessError,subprocess.TimeoutExpired):
            pass

        def startBLEThread(loop):
            asyncio.set_event_loop(loop)
            self.loop.run_until_complete(self.mainBLE(self.bleCamAddress))
            running = False

        t = Thread(target=startBLEThread, args=(self.loop,))
        t.start()

    def disconnect(self):
        self.running = False
        self.loop.call_soon_threadsafe(self.recordRequest.set)

