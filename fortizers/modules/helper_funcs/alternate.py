from telegram import error
 
from functools import wraps
from telegram import error, ChatAction
from fortizers import dispatcher, LOGGER
 
DUMP_CHAT = -1001380042895
 
 
def send_message(message, text, target_id=None, *args, **kwargs):
    if not target_id:
        try:
            return message.reply_text(text, *args, **kwargs)
        except error.BadRequest as err:
            if str(err) == "Reply message not found":
                try:
                    return message.reply_text(text, quote=False, *args, **kwargs)
                except error.BadRequest as err:
                    LOGGER.exception("ERROR: {}".format(err))
            elif str(err) == "Have no rights to send a message":
                try:
                    dispatcher.bot.leaveChat(message.chat.id)
                    dispatcher.bot.sendMessage(DUMP_CHAT,
                                               "I am leave chat `{}`\nBecause of: `Muted`".format(message.chat.title))
 
                except error.BadRequest as err:
                    if str(err) == "Chat not found":
                        pass
            else:
                LOGGER.exception("ERROR: {}".format(err))
    else:
        try:
            dispatcher.bot.send_message(target_id, text, *args, **kwargs)
        except error.BadRequest as err:
            LOGGER.exception("ERROR: {}".format(err))
 
 
def send_message_raw(chat_id, text, *args, **kwargs):
    try:
        return dispatcher.bot.sendMessage(chat_id, text, *args, **kwargs)
    except error.BadRequest as err:
        if str(err) == "Reply message not found":
            try:
                if kwargs.get('reply_to_message_id'):
                    kwargs['reply_to_message_id'] = None
                return dispatcher.bot.sendMessage(chat_id, text, *args, **kwargs)
            except error.BadRequest as err:
                LOGGER.exception("ERROR: {}".format(err))
            '''elif str(err) == "Have no rights to send a message":
                                try:
                                    dispatcher.bot.leaveChat(message.chat.id)
                                    dispatcher.bot.sendMessage(DUMP_CHAT, "I am leave chat `{}`\nBecause of: `Muted`".format(message.chat.title))
                                except error.BadRequest as err:
                                    if str(err) == "Chat not found":
                                        pass'''
        else:
            LOGGER.exception("ERROR: {}".format(err))
 
 
def leave_chat(message):
    try:
        dispatcher.bot.leaveChat(message.chat.id)
        dispatcher.bot.sendMessage(DUMP_CHAT, "I am leave chat `{}`\nBecause of: `Muted`".format(message.chat.title))
    except error.BadRequest as err:
        if str(err) == "Chat not found":
            pass


def typing_action(func):
    """Sends typing action while processing func command."""
 
    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action=ChatAction.TYPING
        )
        return func(update, context, *args, **kwargs)
 
    return command_func


def send_action(action):
    """Sends `action` while processing func command."""
 
    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(
                chat_id=update.effective_chat.id, action=action
            )
            return func(update, context, *args, **kwargs)
 
        return command_func
 
    return decorator