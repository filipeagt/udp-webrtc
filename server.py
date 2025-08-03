import asyncio
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
import cv2
import av

class VideoStreamTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self):
        super().__init__()
        # Recebe stream via UDP (porta 5000)
        self.cap = cv2.VideoCapture("udp://@:5000", cv2.CAP_FFMPEG)

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        ret, frame = self.cap.read()
        if not ret:
            await asyncio.sleep(0.05)
            return await self.recv()

        frame = av.VideoFrame.from_ndarray(frame, format="bgr24")
        frame.pts = pts
        frame.time_base = time_base
        return frame

pcs = set()

async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_state_change():
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    video = VideoStreamTrack()
    pc.addTrack(video)

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.json_response({
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    })

async def on_shutdown(app):
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()

app = web.Application()
app.on_shutdown.append(on_shutdown)
app.router.add_post("/offer", offer)
app.router.add_static("/", ".")

if __name__ == "__main__":
    web.run_app(app, port=8080)
