from pyrogram import filters
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import Config

from helpers.progress import PRGRS
from helpers.tools import clean_up
from helpers.download import download_file, DATA
from helpers.ffmpeg import extract_audio, extract_subtitle


@Client.on_callback_query()
async def cb_handler(client, query):

    if query.data == "start_data":
        await query.answer()
        keyboard = InlineKeyboardMarkup([[
             InlineKeyboardButton("⚔️Update Channel", url="https://t.me/Anime_Warrior_Tamil"),
             InlineKeyboardButton("🛡️Support Group", url="https://t.me/+NITVxLchQhYzNGZl")
             ],[
             InlineKeyboardButton("📢Help", callback_data="help"),
             InlineKeyboardButton("⚡About", callback_data="about")
             ],[
             InlineKeyboardButton("❌Close", callback_data="close")
         ]])

        await query.message.edit_text(
            text=Txt.START_TXT.format(query.from_user.mention),
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        return

    
    elif query.data == "download_file":
        await query.answer()
        await query.message.delete()
        await download_file(client, query.message)


    elif query.data == "progress_msg":
        try:
            msg = "Progress Details...\n\nCompleted : {current}\nTotal Size : {total}\nSpeed : {speed}\nProgress : {progress:.2f}%\nETA: {eta}"
            await query.answer(
                msg.format(
                    **PRGRS[f"{query.message.chat.id}_{query.message.message_id}"]
                ),
                show_alert=True
            )
        except:
            await query.answer(
                "Processing your file...",
                show_alert=True
            )

    elif query.data.startswith('audio'):
        await query.answer()
        try:
            stream_type, mapping, keyword = query.data.split('_')
            data = DATA[keyword][int(mapping)]
            await extract_audio(client, query.message, data)
        except:
            await query.message.edit_text("**Details Not Found**")   


    elif query.data.startswith('subtitle'):
        await query.answer()
        try:
            stream_type, mapping, keyword = query.data.split('_')
            data = DATA[keyword][int(mapping)]
            await extract_subtitle(client, query.message, data)
        except:
            await query.message.edit_text("**Details Not Found**")  


    elif query.data.startswith('cancel'):
        try:
            query_type, mapping, keyword = query.data.split('_')
            data = DATA[keyword][int(mapping)] 
            await clean_up(data['location'])  
            await query.message.edit_text("**Cancelled...**")
            await query.answer(
                "Cancelled...",
                show_alert=True
            ) 
        except:
            await query.answer() 
            await query.message.edit_text("**Details Not Found**")        