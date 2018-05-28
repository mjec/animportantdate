from . import forms
from . import mailouts
from . import models

from django.views.generic import ListView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.utils import timezone


class InviteesView(UserPassesTestMixin, ListView):
    login_url = '/admin/login/'
    model = models.Group
    ordering = ['display_name']
    template_name='wedding/lists/invitations.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.event = kwargs.get('event_id')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.event is not None:
            context['event'] = models.Event.objects.get(id=self.event)
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        if self.event is not None:
            qs = qs.filter(events=self.event)
        return qs

    def test_func(self):
        return self.request.user.is_staff


class AttendeesView(UserPassesTestMixin, ListView):
    login_url = '/admin/login/'
    model = models.Person
    ordering = ['group', 'name']
    template_name='wedding/lists/attendees.html'

    def dispatch(self, request, *args, **kwargs):
        self.event = kwargs.get('event_id')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.event is not None:
            context['event'] = models.Event.objects.get(id=self.event)
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        if self.event is not None:
            qs = qs.filter(group__events=self.event)
        return qs

    def test_func(self):
        return self.request.user.is_staff


class NeedToSendView(UserPassesTestMixin, ListView):
    login_url = '/admin/login/'
    model = models.NeedToSend
    ordering = ['added', 'who__display_name']
    template_name='wedding/lists/need_to_sends.html'
    what = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['what'] = models.NeedToSend.thing_to_send_name(self.what)
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(what=self.what).order_by('-sent', 'added', 'who__display_name')
        return qs

    def test_func(self):
        return self.request.user.is_staff

    @staticmethod
    def view_name_for_type(what):
        if what == models.NeedToSend.INVITATION:
            return 'invitations'
        elif what == models.NeedToSend.THANKYOU_CARD:
            return 'thanks'
        elif what == models.NeedToSend.SAVE_THE_DATE:
            return 'save_the_date'


@staff_member_required
def mark_as_sent(request):
    nts = get_object_or_404(models.NeedToSend, pk=request.GET.get('nts', -1))
    back_url = reverse(NeedToSendView.view_name_for_type(nts.what)) + "#" + request.GET.get('row', '')
    if request.method == 'GET':
        form = forms.MarkAsSentForm(
            instance=nts,
            initial={'sent': timezone.now(), 'sent_note': 'Sent by {}'.format(request.user), 'row': request.GET.get('row', '')}
        )
    else:
        form = forms.MarkAsSentForm(request.POST, instance=nts)
        nts = form.instance
        if form.is_valid():
            nts = form.save()
            return redirect(back_url)

    return render(request, "wedding/mark_as_sent.html", {"form": form, "nts": nts, "back_url": back_url})


@staff_member_required
def mailout(request, mailout_id):

    mailout = models.Mailout.objects.get(id=mailout_id)

    people_already_sent_id = models.MailSent.objects.filter(mailout=mailout).values('recipient__id').distinct()
    # groups_eligible = mailout.event.group_set.all()
    people_eligible = models.Person.objects.filter(group__events=mailout.event, email__isnull=False).exclude(email='')

    initial = {
        "people": people_eligible.exclude(id__in=people_already_sent_id),
    }

    form = forms.DoMailoutForm(
        request.POST or None,
        prefix="mailout",
        initial=initial,
    )

    # Restrict the people who appear to the people who are eligible
    form.fields["people"].queryset = people_eligible

    data = {
        "mailout": mailout,
        "mailout_form": form,
        "body_class": "mailout",
    }

    if request.POST and form.is_valid():
        test_recipient = None
        m = None

        send = form.cleaned_data["action"] == forms.DoMailoutForm.ACTION_SEND_MAIL or form.cleaned_data["action"] == forms.DoMailoutForm.ACTION_SEND_TEST

        if form.cleaned_data["action"] == forms.DoMailoutForm.ACTION_SEND_TEST:
            test_recipient = form.cleaned_data["test_recipient"]
        
        try:
            m = mailouts.MailoutHelper(mailout, form.cleaned_data["people"], test_recipient, send, form.cleaned_data["mark_as_sent"], form.cleaned_data["only_if_unsent"])
            data["mailouts"] = m.messages
        except Exception as e:
            messages.error(request, str(e))

        if m is not None and send:
            try:
                m.send_messages()

                if test_recipient is None:
                    messages.success(request, "The messages have been sent successfully")
                    return redirect('admin:{}_{}_change'.format(mailout._meta.app_label, mailout._meta.model_name), mailout.id)
                else:
                    messages.success(request, "Test messages have been sent successfully to {}".format(test_recipient))
                    return redirect('mailout', mailout.id)

            except Exception as e:
                messages.error(request, str(e))

    return render(request, "wedding/mailout_form.html", data)
