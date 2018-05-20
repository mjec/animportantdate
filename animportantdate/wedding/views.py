from . import forms
from . import mail_alerts
from . import mailouts
from . import models

from django.forms import modelformset_factory
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import mail_managers
from django.shortcuts import redirect, render, reverse
from django.utils import timezone



# Create your views here.

def index(request):

    if get_group(request):
        return guest_details(request)

    auth_form = forms.AuthForm(
        request.GET or None,
        prefix="auth",
    )

    if request.GET and auth_form.is_valid():
        try:
            authenticate(request, auth_form.cleaned_data["pnr"])
            return redirect(guest_details)
        except models.Group.DoesNotExist:
            auth_form.add_error("pnr", "This confirmation code is invalid.")

    data = {
        "auth_form": auth_form,
        "body_class": "home",
    }

    return render(request, "wedding/index.html", data)


def guest_login(request, pnr, open_key):
    try:
        group = authenticate(request, pnr)
        try:
            email = models.MailSent.objects.get(open_key=open_key)
            email.last_opened = timezone.now
            email.save()
            group.add_note('Email {} opened'.format(email.mailout))
        except:
            pass
        return redirect(guest_details)
    except models.Group.DoesNotExist:
        base_url = reverse(index) + "?auth-pnr=%s" % pnr
        return redirect(base_url)


def guest_details(request):

    group = get_group(request)

    group_form = forms.GroupForm(
        request.POST or None,
        instance=group,
        prefix="group",
    )
    #
    # people_in_group = group.person_set.count()
    #
    # PersonFormset = modelformset_factory(
    #     models.Person,
    #     # form=SomeForm
    #     fields=('name', 'email', 'rsvp_status', 'dietary_restrictions'),
    #     extra=0,
    #     min_num=people_in_group, max_num=people_in_group,
    #     validate_min=True, validate_max=True
    # )
    #
    # person_formset = PersonFormset(
    #     request.POST or None,
    #     queryset=group.person_set.all(),
    #     prefix="people"
    # )

    if request.POST and group_form.is_valid(): # and person_formset.is_valid():
        address_changed = False
        if group_form.has_changed():
            if models.Group.contains_address_field(group_form.changed_data):
                address_changed = True
                changed_fields_string = ', '.join(group_form.changed_data)
        group_form.save()
        if address_changed:
            new_invitation_required = models.NeedToSend.objects.filter(who=group, what=models.NeedToSend.INVITATION, sent__isnull=True).count() == 0
            if new_invitation_required:
                group.add_note("Contact details updated ({}) but invitation sent; creating new need to send invitation".format(changed_fields_string))
                models.NeedToSend.objects.create(
                    who=group,
                    what=models.NeedToSend.INVITATION,
                    why="Address changed"
                )
            else:
                group.add_note("Contact details updated ({}); invitation not yet sent".format(changed_fields_string))
            mail_alerts.group_contact_update(group, changed_fields_string, new_invitation_required)
            # person_formset.save()
        messages.success(request, "Thank you! We've got your contact details.")
        return redirect(guest_details)
        

    data = {
        "group_form": group_form,
        # "person_formset": person_formset,
        "group": group,
        "body_class": "guest",
    }

    return render(request, "wedding/guest_details.html", data)


def authenticate(request, pnr):
    group = models.Group.objects.get(pnr=pnr)
    request.session["confirmation_code"] = group.pnr
    return group


def get_group(request):
    if "confirmation_code" in request.session:
        pnr = request.session["confirmation_code"]
        group = models.Group.objects.get(pnr=pnr)
        return group
    else:
        return None


def content_page(request, page_name=None):
    data = {
        "body_class": page_name,
        "group": get_group(request),
    }

    return render(request, "wedding/pages/%s.html" % page_name, data)


def page_not_found(request):
    data = {
        "body_class": "error404",
        "group": get_group(request),
    }

    return render(request, "wedding/pages/error404.html", data, status=404)


@staff_member_required
def mailout(request, mailout_id):

    mailout_id = int(mailout_id)

    mailout = models.Mailout.objects.get(id=mailout_id)

    people_already_sent_id = models.MailSent.objects.filter(mailout=mailout).values('recipient__id').distinct()
    # groups_eligible = mailout.event.group_set.all()
    people_eligible = models.Person.objects.filter(group__events=mailout.event, email__isnull=False)

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
            m = mailouts.MailoutHelper(mailout, form.cleaned_data["people"], test_recipient, send)
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
