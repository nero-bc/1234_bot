from config import Config
from helper.database import db
from pyrogram.types import Message
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
import os, sys, time, asyncio, logging, datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Stats Command Handler
@Client.on_message(filters.command(["stats", "status"]) & filters.user(Config.ADMIN))
async def get_stats(bot, message):
    total_users = await db.total_users_count()
    uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(time.time() - bot.uptime))
    start_t = time.time()
    st = await message.reply('🔍 **Accessing the details...**')
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await st.edit(
        text=(
            f"**--Bot Status--**\n\n"
            f"⌚️ **Bot Uptime:** {uptime}\n"
            f"🐌 **Current Ping:** {time_taken_s:.3f} ms\n"
            f"👥 **Total Users:** {total_users}"
        )
    )

# Restart Command Handler
@Client.on_message(filters.private & filters.command("restart") & filters.user(Config.ADMIN))
async def restart_bot(b, m):
    await m.reply_text("🔄 **Restarting...**")
    os.execl(sys.executable, sys.executable, *sys.argv)

# Broadcast Command Handler
@Client.on_message(filters.command("broadcast") & filters.user(Config.ADMIN) & filters.reply)
async def broadcast_handler(bot: Client, m: Message):
    await bot.send_message(Config.LOG_CHANNEL, f"📣 **{m.from_user.mention} (ID: {m.from_user.id}) has started the broadcast...**")
    all_users = await db.get_all_users()
    broadcast_msg = m.reply_to_message
    sts_msg = await m.reply_text("📤 **Broadcast started...**")
    
    success, failed, done = 0, 0, 0
    start_time = time.time()
    total_users = await db.total_users_count()

    async for user in all_users:
        sts = await send_msg(user['_id'], broadcast_msg)
        if sts == 200:
            success += 1
        else:
            failed += 1
            if sts == 400:
                await db.delete_user(user['_id'])
        
        done += 1
        if done % 20 == 0:
            await sts_msg.edit(
                f"🚀 **Broadcast in progress:**\n"
                f"👥 **Total Users:** {total_users}\n"
                f"✅ **Completed:** {done} / {total_users}\n"
                f"🎉 **Success:** {success}\n"
                f"❌ **Failed:** {failed}"
            )

    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts_msg.edit(
        f"🏁 **Broadcast completed:**\n"
        f"⏱ **Time Taken:** {completed_in}\n\n"
        f"👥 **Total Users:** {total_users}\n"
        f"✅ **Completed:** {done} / {total_users}\n"
        f"🎉 **Success:** {success}\n"
        f"❌ **Failed:** {failed}"
    )

# Function to Send Messages to Users
async def send_msg(user_id, message):
    try:
        await message.copy(chat_id=int(user_id))
        return 200
    except FloodWait as e:
        logger.warning(f"⏳ **FloodWait:** Sleeping for {e.value} seconds")
        await asyncio.sleep(e.value)
        return await send_msg(user_id, message)
    except InputUserDeactivated:
        logger.info(f"🚫 **{user_id} : Deactivated**")
        return 400
    except UserIsBlocked:
        logger.info(f"🚫 **{user_id} : Blocked the bot**")
        return 400
    except PeerIdInvalid:
        logger.info(f"❌ **{user_id} : User ID invalid**")
        return 400
    except Exception as e:
        logger.error(f"⚠️ **Unexpected error with user {user_id}: {e}**")
        return 500
