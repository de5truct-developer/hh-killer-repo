from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SupportTicket, SupportReply
from .forms import SupportTicketForm, SupportReplyForm


@login_required
def support_home(request):
    if request.method == 'POST':
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request, 'Обращение отправлено! Мы ответим в ближайшее время.')
            return redirect('ticket_detail', pk=ticket.pk)
    else:
        form = SupportTicketForm()
    tickets = SupportTicket.objects.filter(user=request.user)
    return render(request, 'support/support_home.html', {'form': form, 'tickets': tickets})


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(SupportTicket, pk=pk)
    # Allow access to owner or admin
    if ticket.user != request.user and not request.user.is_staff:
        messages.error(request, 'Доступ запрещён.')
        return redirect('support_home')

    if request.method == 'POST':
        reply_form = SupportReplyForm(request.POST)
        if reply_form.is_valid():
            reply = reply_form.save(commit=False)
            reply.ticket = ticket
            reply.author = request.user
            reply.is_admin_reply = request.user.is_staff
            reply.save()
            if ticket.status == SupportTicket.STATUS_OPEN and request.user.is_staff:
                ticket.status = SupportTicket.STATUS_IN_PROGRESS
                ticket.save()
            messages.success(request, 'Ответ отправлен.')
            return redirect('ticket_detail', pk=pk)
    else:
        reply_form = SupportReplyForm()

    return render(request, 'support/ticket_detail.html', {
        'ticket': ticket,
        'reply_form': reply_form,
    })


@login_required
def close_ticket(request, pk):
    ticket = get_object_or_404(SupportTicket, pk=pk)
    if ticket.user == request.user or request.user.is_staff:
        ticket.status = SupportTicket.STATUS_CLOSED
        ticket.save()
        messages.success(request, 'Обращение закрыто.')
    return redirect('ticket_detail', pk=pk)


# Admin support panel
@login_required
def admin_support(request):
    if not request.user.is_staff:
        return redirect('home')
    status_filter = request.GET.get('status', '')
    tickets = SupportTicket.objects.all().select_related('user')
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    return render(request, 'support/admin_support.html', {
        'tickets': tickets,
        'status_filter': status_filter,
    })
