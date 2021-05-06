from django.core.exceptions import MultipleObjectsReturned
from django.http import HttpResponse
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage, TemplateSendMessage
from linebot.models.actions import PostbackAction
from linebot.models.events import FollowEvent, MessageEvent, PostbackEvent, UnfollowEvent
from linebot.models.template import ButtonsTemplate

from def_init.secret_settings import *
from .models import LineFriend, User


handler = WebhookHandler(channel_secret=LINE_CHANNEL_SECRET)
line_bot_api = LineBotApi(channel_access_token=LINE_CHANNEL_ACCESS_TOKEN)

def handle_callback(request):
    signature = request.headers['x-line-signature']
    body = request.body.decode('utf-8')
    try:
        handler.handle(body, signature)
        print('successed')
    except InvalidSignatureError:
        print('invalid signature')
        abort(400)

    return HttpResponse()


@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Def initに登録したユーザー名を「名前 (半角スペース)」に続けて入力してください。例）名前 definit')
    )

@handler.add(UnfollowEvent)
def handle_unfollow(event):
    LineFriend.objects.filter(line_user_id=event.source.user_id).delete()

@handler.add(MessageEvent)
def handle_message(event):
    line_user_id = event.source.user_id
    text = event.message.text

    if text == '記事設定':
        article_comment_settings(event)

    elif text == '質問設定':
        answer_settings(event)

    elif text[:3] == '名前 ':
        new_user_name = text[3:]

        user, created = User.objects.get_or_create(username=new_user_name)
        print(user, line_user_id)
        new_friend = LineFriend.objects.get_or_create(user=user, line_user_id=line_user_id)
        line_bot_api.reply_message(event.reply_token, TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                title='Question',
                text='インターン生ですか？',
                actions=[
                    PostbackAction(
                        label='はい、インターン生です',
                        display_text='はい、インターン生です',
                        data='is_intern=True'
                    ),
                    PostbackAction(
                        label='いいえ、ちがいます',
                        display_text='いいえ、ちがいます',
                        data='is_intern=False'
                    ),
                ]
            )
        ))

    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='申し訳ありませんが、このアカウントでは個別のメッセージは受け付けておりません。'))

@handler.add(PostbackEvent)
def handle_postback(event):
    line_user_id = event.source.user_id

    # ユーザー登録
    if event.postback.data == 'is_intern=True':
        new_friend = LineFriend.objects.get(line_user_id=line_user_id)
        new_friend.is_intern = True
        new_friend.save()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='登録が完了しました。記事や質問へのコメントの通知設定を変更するには、それぞれ「記事設定」「質問設定」と入力してください。'))

    elif event.postback.data == 'is_intern=False':
        line_bot_api.reply_message(event.reply_token, TemplateSendMessage(
            alt_text='質問回答担当者ですか？',
            template=ButtonsTemplate(
                title='Question',
                text='質問回答担当者ですか？',
                actions=[
                    PostbackAction(
                        label='はい、質問回答担当者です',
                        display_text='はい、質問回答担当者です',
                        data='is_answerer=True'
                    ),
                    PostbackAction(
                        label='いいえ、ちがいます',
                        display_text='いいえ、ちがいます',
                        data='is_answerer=False'
                    ),
                ]
            )
        ))

    elif event.postback.data == 'is_answerer=True':
        try:
            new_friend = LineFriend.objects.get(line_user_id=event.source.user_id)
            new_friend.is_answerer = True
            new_friend.save()
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='登録が完了しました。記事や質問へのコメントの通知設定を変更するには、それぞれ「記事設定」「質問設定」と入力してください。'))

        except MultipleObjectsReturned:
            line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text='このLINEアカウントとはすでに連携しています。'))

    elif event.postback.data == 'is_answerer=False':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='登録が完了しました。記事や質問へのコメントの通知設定を変更するには、それぞれ「記事設定」「質問設定」と入力してください。'))

    # ここから通知設定（記事へのコメント）
    elif event.postback.data == 'notify_comment=True':
        setting = LineFriend.objects.get(line_user_id=event.source.user_id)
        setting.notify_comment = True
        setting.save()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='記事へのコメント通知はオンになっています。'))

    elif event.postback.data == 'notify_comment=False':
        setting = LineFriend.objects.get(line_user_id=event.source.user_id)
        setting.notify_comment = False
        setting.save()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='記事へのコメント通知はオフになっています。'))

    # 通知設定（質問へのコメント）
    elif event.postback.data == 'notify_answer=True':
        setting = LineFriend.objects.get(line_user_id=event.source.user_id)
        setting.notify_answer = True
        setting.save()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='質問への回答やコメントの通知はオンになっています。'))

    elif event.postback.data == 'notify_answer=False':
        setting = LineFriend.objects.get(line_user_id=event.source.user_id)
        setting.notify_answer = False
        setting.save()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='質問への回答やコメントの通知はオフになっています。'))

    else:
        print('無効なデータ送信です。')

def article_comment_settings(event):
    user = LineFriend.objects.get(line_user_id=event.source.user_id)
    if user.notify_comment:
        text_change = '通知をやめる'
        data_change = 'notify_comment=False'
        text_keep = '変更しない'
        data_keep = 'notify_comment=True'
    elif not user.notify_comment:
        text_change = '通知する'
        data_change = 'notify_comment=True'
        text_keep = '変更しない'
        data_keep = 'notify_comment=False'

    line_bot_api.reply_message(event.reply_token, TemplateSendMessage(
            alt_text='LINE通知設定',
            template=ButtonsTemplate(
                title='記事へのコメント通知設定',
                text='記事へのコメントの通知設定を変更しますか？',
                actions=[
                    PostbackAction(
                        label=text_change,
                        display_text=text_change,
                        data=data_change,
                    ),
                    PostbackAction(
                        label=text_keep,
                        display_text=text_keep,
                        data=data_keep,
                    ),
                ]
            )
        ))

def answer_settings(event):
    user = LineFriend.objects.get(line_user_id=event.source.user_id)
    if user.notify_answer:
        text_change = '通知をやめる'
        data_change = 'notify_answer=False'
        text_keep = '変更しない'
        data_keep = 'notify_answer=True'

    elif not user.notify_answer:
        text_change = '通知する'
        data_change = 'notify_answer=True'
        text_keep = '変更しない'
        data_keep = 'notify_answer=False'

    line_bot_api.reply_message(event.reply_token, TemplateSendMessage(
            alt_text='LINE通知設定',
            template=ButtonsTemplate(
                title='質問への回答・コメント通知設定',
                text='質問への回答やコメントの通知設定を変更しますか？',
                actions=[
                    PostbackAction(
                        label=text_change,
                        display_text=text_change,
                        data=data_change,
                    ),
                    PostbackAction(
                        label=text_keep,
                        display_text=text_keep,
                        data=data_keep,
                    ),
                ]
            )
        ))
