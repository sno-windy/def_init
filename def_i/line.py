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
        TextSendMessage(text='【登録はまだ完了していません】Def initに登録したユーザー名を「名前 (半角スペース)」に続けて入力してください。例）名前 definit')
    )

@handler.add(UnfollowEvent)
def handle_unfollow(event):
    LineFriend.objects.filter(line_user_id=event.source.user_id).delete()
    print('deleted')

@handler.add(MessageEvent)
def handle_message(event):
    print('id:', event.source.user_id)
    line_user_id = event.source.user_id
    text = event.message.text

    # if text == '記事設定':
    #     article_comment_settings(event)

    # elif text == '質問設定':
    #     answer_settings(event)

    if text == '設定':
        choose_settings(event)

    elif text[:3] == '名前 ':
        new_user_name = text[3:]

        user, created = User.objects.get_or_create(username=new_user_name)
        print(user, line_user_id)
        new_friend = LineFriend.objects.get_or_create(user=user, line_user_id=line_user_id)
        change_position(event)

    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='申し訳ありませんが、このアカウントでは個別のメッセージは受け付けておりません。'))

@handler.add(PostbackEvent)
def handle_postback(event):
    line_user_id = event.source.user_id

    # ユーザー登録
    if event.postback.data == 'is_intern=True':
        try:
            new_friend = LineFriend.objects.get(line_user_id=line_user_id)
            new_friend.is_intern = True
            new_friend.is_answerer = False
            new_friend.save()
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='設定を完了しました。変更するには、「設定」と入力してください。')
            )
        except MultipleObjectsReturned:
            line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text='このLINEアカウントとはすでに連携しています。'))

    elif event.postback.data == 'is_answerer=True':
        try:
            new_friend = LineFriend.objects.get(line_user_id=event.source.user_id)
            new_friend.is_intern = False
            new_friend.is_answerer = True
            new_friend.save()
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='設定を完了しました。変更するには、「設定」と入力してください。')
            )

        except MultipleObjectsReturned:
            line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text='このLINEアカウントとはすでに連携しています。'))

    elif event.postback.data == 'position=others':
        try:
            new_friend = LineFriend.objects.get(line_user_id=event.source.user_id)
            new_friend.is_intern = False
            new_friend.is_answerer = False
            new_friend.save()
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='設定を完了しました。変更するには、「設定」と入力してください。')
            )

        except MultipleObjectsReturned:
            line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text='このLINEアカウントとはすでに連携しています。'))

    # ここから通知設定（記事へのコメント）
    elif event.postback.data == 'notify_comment=True':
        setting = LineFriend.objects.get(line_user_id=event.source.user_id)
        setting.notify_comment = True
        setting.save()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='記事へのコメント通知はオンになっています。')
        )

    elif event.postback.data == 'notify_comment=False':
        setting = LineFriend.objects.get(line_user_id=event.source.user_id)
        setting.notify_comment = False
        setting.save()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='記事へのコメント通知はオフになっています。')
        )

    # 通知設定（質問へのコメント）
    elif event.postback.data == 'notify_answer=True':
        setting = LineFriend.objects.get(line_user_id=event.source.user_id)
        setting.notify_answer = True
        setting.save()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='質問への回答やコメントの通知はオンになっています。')
        )

    elif event.postback.data == 'notify_answer=False':
        setting = LineFriend.objects.get(line_user_id=event.source.user_id)
        setting.notify_answer = False
        setting.save()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='質問への回答やコメントの通知はオフになっています。')
        )

    elif event.postback.data == 'change_position':
        change_position(event)

    elif event.postback.data == 'article_comment_settings':
        article_comment_settings(event)

    elif event.postback.data == 'answer_settings':
        answer_settings(event)

    else:
        print('無効なデータ送信です。')

def choose_settings(event):
    user = LineFriend.objects.get(line_user_id=event.source.user_id)
    line_bot_api.reply_message(
        event.reply_token, TemplateSendMessage(
            alt_text='設定',
            template=ButtonsTemplate(
                title='設定',
                text='変更したい設定を選択してください。',
                actions=[
                    PostbackAction(
                        label='記事へのコメントの通知設定',
                        display_text='記事へのコメントの通知設定',
                        data='article_comment_settings',
                    ),
                    PostbackAction(
                        label='質問へのコメントの通知設定',
                        display_text='質問へのコメントの通知設定',
                        data='answer_settings',
                    ),
                    PostbackAction(
                        label='ポジション設定',
                        display_text='ポジション設定',
                        data='change_position',
                    ),
                ]
            )
        )
    )


def article_comment_settings(event):
    user = LineFriend.objects.get(line_user_id=event.source.user_id)
    if user.notify_comment:
        text_on = '通知をON（現在のまま）'
        text_off = '通知をOFF'
    elif not user.notify_comment:
        text_on = '通知をON'
        text_off = '通知をOFF（現在のまま）'

    line_bot_api.reply_message(event.reply_token, TemplateSendMessage(
            alt_text='LINE通知設定',
            template=ButtonsTemplate(
                title='記事へのコメント通知設定',
                text='記事へのコメントの通知設定を変更しますか？',
                actions=[
                    PostbackAction(
                        label=text_on,
                        display_text=text_on,
                        data='notify_comment=True',
                    ),
                    PostbackAction(
                        label=text_off,
                        display_text=text_off,
                        data='notify_comment=False',
                    ),
                ]
            )
        ))

def answer_settings(event):
    user = LineFriend.objects.get(line_user_id=event.source.user_id)
    if user.notify_answer:
        text_on = '通知をON（現在のまま）'
        text_off = '通知をOFF'

    elif not user.notify_answer:
        text_on = '通知をON'
        text_off = '通知をOFF（現在のまま）'

    line_bot_api.reply_message(event.reply_token, TemplateSendMessage(
            alt_text='LINE通知設定',
            template=ButtonsTemplate(
                title='質問への回答・コメント通知設定',
                text='質問への回答やコメントの通知設定を変更しますか？',
                actions=[
                    PostbackAction(
                        label=text_on,
                        display_text=text_on,
                        data='notify_answer=True',
                    ),
                    PostbackAction(
                        label=text_off,
                        display_text=text_off,
                        data='notify_answer=False',
                    ),
                ]
            )
        ))

def change_position(event):
    user = LineFriend.objects.get(line_user_id=event.source.user_id)
    line_bot_api.reply_message(event.reply_token, TemplateSendMessage(
            alt_text='ポジション設定',
            template=ButtonsTemplate(
                title='ポジション設定',
                text='あなたのポジションを選択してください。',
                actions=[
                    PostbackAction(
                        label='インターン生',
                        display_text='インターン生',
                        data='is_intern=True',
                    ),
                    PostbackAction(
                        label='質問回答担当',
                        display_text='質問回答担当',
                        data='is_answerer=True',
                    ),
                    PostbackAction(
                        label='その他',
                        display_text='その他',
                        data='position=others',
                    ),

                ]
            )
        ))
