from pyrogram import filters
from pyrogram import Client
from plugins import start 
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from plugins.audio import remove_audio, trim_video

from config import Config


@Client.on_message(filters.private & (filters.document | filters.video))
async def confirm_dwnld(client, message):
    media = message
    filetype = media.document or media.video

    if filetype.mime_type.startswith("video/"):
        await message.reply_text(
            "**What do you want me to do 🤔**",
            quote=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text="DOWNLOAD and PROCESS", callback_data="download_file")],
                [InlineKeyboardButton(text="Remove Audio🎧", callback_data="handle_remove_audio")],
                [InlineKeyboardButton(text="Trim Video ✂️", callback_data="handle_trim_video")],
                [InlineKeyboardButton(text="CANCEL", callback_data="close")]
            ])
        )
    else:
        await message.reply_text(
            "Invalid Media",
            quote=True
        )

    elif data == "close":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
            await query.message.continue_propagation()
        except:
            await query.message.delete()
            await query.message.continue_propagation()
