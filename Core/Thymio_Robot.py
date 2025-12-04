from Core.Thymio_Interface import RobotInterface
from tdmclient import ClientAsync
import asyncio

class RealThymio(RobotInterface):
   
    def __init__(self):
        # Connect to Thymio Device Manager
        self.client = ClientAsync()
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self._connect())

        self.x = 0
        self.y = 0
        self.theta = 0

    async def _connect(self):
        await self.client.connect()
        self.node = await self.client.wait_for_node()





    # ---------------- Movement primitives ----------------
    def move_forward(self):
        self._send_event("forward")

    def move_backward(self):
        self._send_event("half_back")

    def rotate_left(self):
        self._send_event("left")

    def rotate_right(self):
        self._send_event("right")

    def find_block(self):
        # Example placeholder
        print("Block detection not implemented.")

    def stop(self):
        self._send_event("stop")



    # ---------------- Helpers ----------------
    def _send_event(self, event_name):
        async def _inner():
            await self.node.send_event(event_name)
            # Wait for 'performed' callback
            await self.client.wait_for_event("performed", timeout=5.0)
        self.loop.run_until_complete(_inner())


    def update(self, dt):
        # No continuous simulation needed
        pass

    def get_position(self):
        return self.x, self.y, self.theta

    def set_grid(self, grid):
        print("Grid set in RealThymio (ignored).")

    def set_path(self, path):
        print("Path set in RealThymio (ignored).")

    def set_block_manager(self, block_manager):
        print("Block manager set in RealThymio (ignored).")

