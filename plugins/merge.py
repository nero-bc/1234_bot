import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import subprocess
import time
from config import Config
from progress import progress

DOWNLOAD_DIR = "/content/Drive_bot/Drive_bot/downloads/"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

user_media_files = {}
user_merge_mode = {}

@Client.on_message(filters.command("merge_audio"))
async def set_merge_audio(client, message: Message):
    user_id = message.from_user.id
    user_merge_mode[user_id] = "audio"
    user_media_files[user_id] = []
    await message.reply_text("Send the first audio file.")

@Client.on_message(filters.command("merge_video"))
async def set_merge_video(client, message: Message):
    user_id = message.from_user.id
    user_merge_mode[user_id] = "video"
    user_media_files[user_id] = []
    await message.reply_text("Send the video file.")

@Client.on_message((filters.video | filters.audio) & ~filters.forwarded)
async def receive_media(client, message: Message):
    user_id = message.from_user.id

    if user_id not in user_merge_mode:
        await message.reply_text("Please use /merge_audio or /merge_video to start the merging process.")
        return

    merge_mode = user_merge_mode[user_id]
    media_type = 'audio' if message.audio else 'video'
    media_file = getattr(message, media_type)

    start_time = time.time()
    progress_message = await message.reply_text(f"Downloading {media_type}...")

    try:
        media_path = await message.download(
            file_name=f"{DOWNLOAD_DIR}{media_file.file_name}",
            progress=progress,
            progress_args=(progress_message, start_time, f"Downloading {media_type}")
        )

        user_media_files[user_id].append(media_path)

        if merge_mode == "audio":
            if len(user_media_files[user_id]) == 1:
                await progress_message.edit_text("First audio received. Now send the second audio.")
            elif len(user_media_files[user_id]) == 2:
                await progress_message.edit_text("Both audios received. Merging them now...")
                await merge_audios(client, message, user_id)
        elif merge_mode == "video":
            if len(user_media_files[user_id]) == 1 and media_type == "video":
                await progress_message.edit_text("Video received. Now send the audio file.")
            elif len(user_media_files[user_id]) == 2 and any('.mp4' in file for file in user_media_files[user_id]):
                await progress_message.edit_text("Both video and audio received. Merging them now...")
                await merge_video_and_audio(client, message, user_id)
    except Exception as e:
        await progress_message.edit_text(f"Error during download: {e}")

async def merge_audios(client, message, user_id):
    audio1, audio2 = user_media_files[user_id]
    output_path = f"{DOWNLOAD_DIR}merged_audio_{user_id}.mp3"

    command = [
        "ffmpeg",
        "-y",  # Add the '-y' flag to overwrite existing files
        "-i", audio1,
        "-i", audio2,
        "-filter_complex", "[0:0][1:0]concat=n=2:v=0:a=1[out]",
        "-map", "[out]",
        output_path
    ]

    start_time = time.time()
    progress_message = await message.reply_text("Merging audio files...")

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        if os.path.exists(output_path):
            await progress_message.edit_text("Merging complete, uploading the merged audio...")
            try:
                await message.reply_document(
                    document=output_path,
                    caption="Here is your merged audio file!",
                    progress=progress,
                    progress_args=(progress_message, start_time, "Uploading merged audio")
                )
            except Exception as e:
                await progress_message.edit_text(f"Failed to upload the merged audio: {e}")
        else:
            await progress_message.edit_text("Merging completed, but the output file was not found.")
    else:
        await progress_message.edit_text(f"Failed to merge: {stderr.decode()}")

    # Clean up
    os.remove(audio1)
    os.remove(audio2)
    if os.path.exists(output_path):
        os.remove(output_path)

    # Remove user data
    del user_media_files[user_id]
    del user_merge_mode[user_id]

async def merge_video_and_audio(client, message, user_id):
    video, audio = user_media_files[user_id]
    output_path = f"{DOWNLOAD_DIR}merged_video_{user_id}.mp4"

    command = [
        "ffmpeg",
        "-y",  # Add the '-y' flag to overwrite existing files
        "-i", video,
        "-i", audio,
        "-c:v", "copy",
        "-c:a", "aac",
        "-strict", "experimental",
        "-map", "0:v:0",
        "-map", "1:a:0",
        output_path
    ]

    start_time = time.time()
    progress_message = await message.reply_text("Merging video and audio...")

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        if os.path.exists(output_path):
            await progress_message.edit_text("Merging complete, uploading the merged video...")
            try:
                await message.reply_document(
                    document=output_path,
                    caption="Here is your merged video file!",
                    progress=progress,
                    progress_args=(progress_message, start_time, "Uploading merged video")
                )
            except Exception as e:
                await progress_message.edit_text(f"Failed to upload the merged video: {e}")
        else:
            await progress_message.edit_text("Merging completed, but the output file was not found.")
    else:
        await progress_message.edit_text(f"Failed to merge: {stderr.decode()}")

    # Clean up
    os.remove(video)
    os.remove(audio)
    if os.path.exists(output_path):
        os.remove(output_path)

    # Remove user data
    del user_media_files[user_id]
    del user_merge_mode[user_id]

@Client.on_message(filters.command("cancel"))
async def cancel(client, message: Message):
    user_id = message.from_user.id
    if user_id in user_media_files:
        del user_media_files[user_id]
    if user_id in user_merge_mode:
        del user_merge_mode[user_id]
    await message.reply_text("Merging process has been cancelled.")
