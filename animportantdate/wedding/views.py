from . import forms
from . import mail_alerts
from . import models

from django.forms import modelformset_factory
from django.contrib import messages
from django.shortcuts import redirect, render, reverse
from django.utils import timezone

from django.views.decorators.vary import vary_on_cookie
from django.views.decorators.cache import never_cache, cache_control, patch_cache_control


@vary_on_cookie
def index(request):

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

    response = render(request, "wedding/index.html", data)
    if request.GET:
        patch_cache_control(response, private=True, max_age=60)
    else:
        patch_cache_control(response, public=True, max_age=3600)
    return response


@never_cache
def guest_login(request, pnr, open_key, destination='details'):
    try:
        group = authenticate(request, pnr)
        try:
            email = models.MailSent.objects.get(open_key=open_key)
            email.last_opened = timezone.now()
            email.save()
            group.add_note('Email {} opened'.format(email.mailout))
        except:
            pass
        if destination == 'index':
            return redirect(index)
        else:
            return redirect(guest_details)
    except models.Group.DoesNotExist:
        base_url = reverse(index) + "?auth-pnr=%s" % pnr
        return redirect(base_url)


@never_cache
def guest_details(request):

    group = get_group(request)
    if group is None:
        return redirect(reverse('details'))

    group_form = forms.GroupForm(
        request.POST or None,
        instance=group,
        prefix="group",
    )

    people_in_group = group.person_set.count()

    if models.SiteConfiguration.get_solo().accepting_rsvps:
        person_formset_fields = (
            'name', 'email', 'dietary_restrictions', 'rsvp_status', )
    else:
        person_formset_fields = ('name', 'email', 'dietary_restrictions', )

    def formfield_callback_method(field, **kwargs):
        formfield = field.formfield(**kwargs)
        if field.name == 'rsvp_status':
            # We want to prohibit folks from saving a non-RSVP
            formfield.choices = [
                c for c in models.Person.RSVP_CHOICES if c[0] != models.Person.RSVP_UNKNOWN]
        return formfield

    PersonFormset = modelformset_factory(
        models.Person,
        fields=person_formset_fields,
        formfield_callback=formfield_callback_method,
        extra=0,
        min_num=people_in_group,
        max_num=people_in_group,
        validate_min=True,
        validate_max=True
    )

    person_formset = PersonFormset(
        request.POST or None,
        queryset=group.person_set.all(),
        prefix="people"
    )

    if request.POST and group_form.is_valid() and person_formset.is_valid():
        address_changed = False
        if group_form.has_changed():
            if models.Group.contains_address_field(group_form.changed_data):
                address_changed = True
                changed_fields_string = ', '.join(group_form.changed_data)
        group_form.save()
        if address_changed:
            new_invitation_required = models.NeedToSend.objects.filter(
                who=group, what=models.NeedToSend.INVITATION, sent__isnull=True).count() == 0
            if new_invitation_required:
                group.add_note("Contact details updated ({}) but invitation sent; creating new need to send invitation".format(
                    changed_fields_string))
                models.NeedToSend.objects.create(
                    who=group,
                    what=models.NeedToSend.INVITATION,
                    why="Address changed"
                )
            else:
                group.add_note("Contact details updated ({}); invitation not yet sent".format(
                    changed_fields_string))
            mail_alerts.group_contact_update(
                group, changed_fields_string, new_invitation_required)
        person_formset.save()
        messages.success(request, "Thank you! We've got your contact details.")
        return redirect(guest_details)

    data = {
        "group_form": group_form,
        "person_formset": person_formset,
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


@vary_on_cookie
@cache_control(max_age=3600, public=True)
def content_page(request, page_name=None):
    data = {
        "body_class": page_name,
        "group": get_group(request),
    }

    return render(request, "wedding/pages/%s.html" % page_name, data)


@vary_on_cookie
@cache_control(max_age=3600, public=True)
def photos(request):
    data = {
        "body_class": "photos",
        "group": get_group(request),
        "photos": models.Photo.objects.all(),
    }

    return render(request, "wedding/pages/photos.html", data)


@vary_on_cookie
@cache_control(max_age=3600, public=True)
def page_not_found(request):
    data = {
        "body_class": "error404",
        "group": get_group(request),
    }

    return render(request, "wedding/pages/error404.html", data, status=404)
