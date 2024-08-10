import os
import time
import math
import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from helper.database import db
from config import Config, Txt

@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):
    user = message.from_user
    
    # Add user to the database
    await db.add_user(client, message)
    
    # Create inline keyboard buttons
    button = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚔️ Update Channel", url="https://t.me/Anime_Warrior_Tamil"),
            InlineKeyboardButton("🛡️ Support Group", url="https://t.me/+NITVxLchQhYzNGZl")
        ],
        [
            InlineKeyboardButton("📢 Help", callback_data="help"),
            InlineKeyboardButton("⚡ About", callback_data="about")
        ],
        [
            InlineKeyboardButton("❌ Close", callback_data="close")
        ]
    ])
    
    # Send start message with or without a photo
    if Config.START_PIC:
        await message.reply_photo(Config.START_PIC, 
                                 caption=Txt.START_TXT.format(user.mention), 
                                 reply_markup=button)
    else:
        await message.reply_text(text=Txt.START_TXT.format(user.mention), 
                                 reply_markup=button, 
                                 disable_web_page_preview=True)

@Client.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    data = query.data
    
    # Handle different callback query data
    if data == "start":
        await query.message.edit_text(
            text=Txt.START_TXT.format(query.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("⚔️ Update Channel", url="https://t.me/Anime_Warrior_Tamil"),
                    InlineKeyboardButton("🛡️ Support Group", url="https://t.me/+NITVxLchQhYzNGZl")
                ],
                [
                    InlineKeyboardButton("📢 Help", callback_data="help"),
                    InlineKeyboardButton("⚡ About", callback_data="about")
                ],
                [
                    InlineKeyboardButton("❌ Close", callback_data="close")
                ]
            ])
        )
        
    elif data == "help":
        await query.message.edit_text(
            text=Txt.HELP_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("😈 Owner", url="https://t.me/Devilo7")
                ],
                [
                    InlineKeyboardButton("❌ Close", callback_data="close"),
                    InlineKeyboardButton("⏪ Back", callback_data="start")
                ]
            ])
        )
        
    elif data == "about":
        await query.message.edit_text(
            text=Txt.ABOUT_TXT.format(client.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("😈 Owner", url="https://t.me/Devilo7")
                ],
                [
                    InlineKeyboardButton("❌ Close", callback_data="close"),
                    InlineKeyboardButton("⏪ Back", callback_data="start")
                ]
            ])
        )
        
    elif data == "close":
        try:
            # Attempt to delete the message and reply to message
            await query.message.delete()
            if query.message.reply_to_message:
                await query.message.reply_to_message.delete()
            await query.message.continue_propagation()
        except:
            # Fallback if deletion fails
            await query.message.delete()
            await query.message.continue_propagation()
