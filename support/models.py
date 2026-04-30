from django.db import models
from users.models import User


class SupportTicket(models.Model):
    STATUS_OPEN = 'open'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Открыт'),
        (STATUS_IN_PROGRESS, 'В обработке'),
        (STATUS_CLOSED, 'Закрыт'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    subject = models.CharField(max_length=200, verbose_name='Тема')
    message = models.TextField(verbose_name='Сообщение')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Тикет поддержки'
        verbose_name_plural = 'Тикеты поддержки'

    def __str__(self):
        return f'#{self.pk} {self.subject} ({self.user.email})'


class SupportReply(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_replies')
    message = models.TextField(verbose_name='Ответ')
    created_at = models.DateTimeField(auto_now_add=True)
    is_admin_reply = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Ответ поддержки'
        verbose_name_plural = 'Ответы поддержки'

    def __str__(self):
        return f'Ответ на тикет #{self.ticket_id}'
