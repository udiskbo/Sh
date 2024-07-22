import os
import cv2
import asyncio
from moviepy.editor import VideoFileClip
from pyrogram import Client

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")
video_dir = os.getenv("VIDEO_DIR")

async def upload_video(client, video_path):
    vid = cv2.VideoCapture(video_path)
    clip = VideoFileClip(video_path)

    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    duration = clip.duration

    success, image = vid.read()
    success, image = vid.read()
    height, width, channels = image.shape
    r = 320 / width
    max_size = (320, int(height * r))
    thumb = cv2.resize(image , max_size, interpolation=cv2.INTER_AREA)
    thumb_path = "/tmp/thumb.jpeg"
    cv2.imwrite(thumb_path, thumb)

    await client.send_video(chat_id, video_path, duration=int(duration)+1, width=int(width), height=int(height), thumb=thumb_path)

    clip.close()
    vid.release()

async def main():
    async with Client("my_bot", api_id, api_hash, bot_token=bot_token) as app:
        video_files = [f for f in os.listdir(video_dir) if f.endswith(('.mp4', '.avi', '.mkv'))]
        for video_file in video_files:
            video_path = os.path.join(video_dir, video_file)
            await upload_video(app, video_path)

if __name__ == "__main__":
    asyncio.run(main())
