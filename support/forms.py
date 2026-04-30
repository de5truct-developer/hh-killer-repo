from django import forms
from .models import SupportTicket, SupportReply


class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ('subject', 'message')
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': 'Кратко опишите проблему...'}),
            'message': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Подробно опишите вашу проблему или вопрос...',
            }),
        }
        labels = {
            'subject': 'Тема обращения',
            'message': 'Сообщение',
        }


class SupportReplyForm(forms.ModelForm):
    class Meta:
        model = SupportReply
        fields = ('message',)
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Ваш ответ...',
            }),
        }
        labels = {
            'message': 'Ответить',
        }
