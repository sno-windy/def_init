# import os, sys
# sys.path.append(os.pardir)

# from linebot import LineBotApi, WebhookHandler
# from linebot.models import TextSendMessage

# from def_init import secret_settings
# from .models import LineFriend


# handler = WebhookHandler(channel_secret=secret_settings.LINE_CHANNEL_SECRET)

# def notify_new_question():
#     line_bot_api = LineBotApi(channel_access_token=secret_settings.LINE_CHANNEL_ACCESS_TOKEN)
#     notify_to = LineFriend.objects.filter(is_answerer=True)
#     print("to:", notify_to)
#     for push in notify_to:
#         line_bot_api.push_message(push.line_user_id, TextSendMessage(text="質問が投稿されました。回答をお願いします。"))
