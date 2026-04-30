from django.contrib import admin
from .models import SupportTicket, SupportReply


class SupportReplyInline(admin.TabularInline):
    model = SupportReply
    extra = 1
    readonly_fields = ('created_at',)


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'user', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'user__email', 'message')
    inlines = [SupportReplyInline]
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SupportReply)
class SupportReplyAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'author', 'is_admin_reply', 'created_at')
    list_filter = ('is_admin_reply',)
