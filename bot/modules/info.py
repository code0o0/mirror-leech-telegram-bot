from pyrogram.handlers import MessageHandler
from pyrogram.filters import command
from pyrogram.enums import ChatType
from html import escape

from bot import bot, user, user_data, OWNER_ID, LOGGER
from bot.helper.telegram_helper.message_utils import auto_delete_message, sendMessage
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.ext_utils.bot_utils import new_task


@new_task
async def info(client, message):
    msg = ''
    operator_user = message.from_user or message.sender_chat
    operator_id = operator_user.id
    text = message.text.split()[1] if len(message.text.split()) > 1 else None
    tgclient = user or bot
    if operator_id in user_data and user_data[operator_id].get('is_sudo'):
        is_sudo = True
    elif operator_id == OWNER_ID:
        is_sudo = True
    else:
        is_sudo = False
    if all([text, is_sudo]):
        if text.isdigit():
            queried_id = int(text)
        else:
            text = text.split('t.me/')[-1]
            queried_id = text if text.startswith('@') else f'@{text}'
        try:
            queried_chat = await tgclient.get_chat(queried_id)
            chat_id = queried_chat.id
            chat_name = queried_chat.username or f"{queried_chat.first_name} {queried_chat.last_name}" or "Unknown"
            phone_number = queried_chat.phone_number if hasattr(queried_chat, 'phone_number') else None
            chat_type = queried_chat.type
            dc_id = queried_chat.dc_id
        except Exception as e:
            LOGGER.error(e)
        else:
            msg += "<b>Chat Information</b>\n"
            msg += f'<pre>ID: <code>{chat_id}</code></pre>\n'
            msg += f'<pre>Name: @{escape(chat_name)}</pre>\n'
            if phone_number:
                msg += f'<pre>Phone: {phone_number}</pre>\n'
            msg += f'<pre>Type: {chat_type}</pre>\n'
            msg += f'<pre>DC-ID: DC-{dc_id}</pre>\n'
        if not msg:
            msg += f'<b>Chat not found!</b>\n'
            msg += f'<b>Note: </b>If you want to query the group information, please add the bot to the group first!\n'
    elif all([is_sudo, message.reply_to_message]):
        origin_message = message.reply_to_message
        if from_user := origin_message.forward_from:
            queried_id = from_user.id
            username = from_user.username or from_user.mention
            dc_id = from_user.dc_id
            msg += f'<pre>User: @{escape(username)}</pre>\n'
            msg += f'<pre>User-ID: <code>{queried_id}</code></pre>\n'
            msg += f'<pre>DC-ID: DC-{dc_id}</pre>\n\n'
        elif from_user := origin_message.forward_sender_name:
            msg += f'<pre>User: {escape(from_user)}</pre>\n'
        if chat := origin_message.forward_from_chat:
            chat_title = chat.title
            chat_id = chat.id
            chat_name = chat.username or "Unknown"
            dc_id = chat.dc_id
            distance = chat.distance
            msg += f'<pre>Chat-Title: {escape(chat_title)}</pre>\n'
            msg += f'<pre>Chat-ID: <code>{chat_id}</code></pre>\n'
            msg += f'<pre>Chat-Name: @{escape(chat_name)}</pre>\n'
            msg += f'<pre>DC-ID: DC-{dc_id}</pre>\n'
            msg += f'<pre>Distance: {distance}</pre>\n'
        if message_id := origin_message.forward_from_message_id:
            msg += f'<pre>Message-ID: </b><code>{message_id}</code></pre>\n'
        else:
            msg += f'<pre>Message-ID: </b><code>{origin_message.id}</code></pre>\n'
        if message_group_id := origin_message.media_group_id:
            msg += f'<pre>Message-GID: </b><code>{message_group_id}</code></pre>\n'
        if date := origin_message.forward_date:
            msg += f'<pre>Date: </b><code>{date.strftime("%Y-%m-%d %H:%M:%S")}</code></pre>\n'
        else:
            msg += f'<pre>Date: </b><code>{origin_message.date.strftime("%Y-%m-%d %H:%M:%S")}</code></pre>\n'
        media = getattr(origin_message, origin_message.media.value) if origin_message.media else None
        if media:
            file_id = media.file_id
            msg += f'<pre>File-ID: <code>{file_id}</code></pre>\n'
        if not msg:
            msg += '<b>Unable to obtain valid information, it may be due to the user setting privacy protection or invalid reply messages!</b>\n'
    else:
        from_user = message.from_user or message.sender_chat
        queried_id = from_user.id
        username = from_user.username or from_user.mention
        dc_id = from_user.dc_id
        msg += "<b>User Information</b>\n"
        msg += f'<pre>User: @{escape(username)}</pre>\n'
        msg += f'<pre>User-ID: <code>{queried_id}</code></pre>\n'
        msg += f'<pre>DC-ID: DC-{dc_id}</pre>\n\n'
        chat = message.chat
        if chat.type in [ChatType.SUPERGROUP, ChatType.GROUP] and is_sudo:
            group_title = chat.title
            group_id = chat.id
            group_name = chat.username or "Unknown"
            dc_id = chat.dc_id
            distance = chat.distance
            msg += f'<pre>Group-Title: {escape(group_title)}</pre>\n'
            msg += f'<pre>Group-ID: <code>{group_id}</code></pre>\n'
            msg += f'<pre>Group-Name: @{escape(group_name)}</pre>\n'
            msg += f'<pre>DC-ID: DC-{dc_id}</pre>\n'
            msg += f'<pre>Distance: {distance}</pre>\n'
    
    reply_message = await sendMessage(message, msg)
    await auto_delete_message(message, reply_message, delay=20)

bot.add_handler(MessageHandler(info, filters=command(BotCommands.InfoCommand) & CustomFilters.authorized))
