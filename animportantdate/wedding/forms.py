from . import models
from django import forms
import re


class AuthForm(forms.Form):

    pnr = forms.CharField(
        max_length=10,
        label="Confirmation code",
    )


class MarkAsSentForm(forms.ModelForm):
    row = forms.CharField(required=False, empty_value=None,
                          widget=forms.HiddenInput)

    class Meta:
        model = models.NeedToSend
        fields = [
            "sent",
            "sent_note",
        ]


class GroupForm(forms.ModelForm):

    class Meta:
        model = models.Group
        fields = [
            "telephone",
            "address_1",
            "address_2",
            "address_city",
            "address_state_province",
            "address_postal_code",
            "address_country",
        ]

    def make_required(self, field):
        self.fields[field].required = True

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        required_fields = [
            "address_1",
            "address_city",
            "address_postal_code",
            "address_country",
            "telephone",
        ]
        for i in required_fields:
            self.make_required(i)
        self.fields["address_state_province"].required = False

    def clean(self):
        cleaned_data = super(GroupForm, self).clean()
        if cleaned_data.get("address_country") == "AU":
            if re.match(r"\d{4}$", cleaned_data.get("address_postal_code")) is None:
                self.add_error("address_postal_code",
                               "Australian post codes must be four digits")
            if cleaned_data.get("address_state_province") == "":
                self.add_error("address_state_province",
                               "State required in Australia")
        elif cleaned_data.get("address_country") == "US":
            if cleaned_data.get("address_state_province") == "":
                self.add_error("address_state_province",
                               "State required in USA")

        return cleaned_data


class DoMailoutForm(forms.Form):
    ACTION_PREVIEW = 1
    ACTION_SEND_MAIL = 2
    ACTION_SEND_TEST = 3

    ACTIONS = (
        (ACTION_PREVIEW, "Preview"),
        (ACTION_SEND_TEST, "Send test"),
        (ACTION_SEND_MAIL, "Send mailout"),
    )

    people = forms.ModelMultipleChoiceField(queryset=models.Person.objects)
    action = forms.TypedChoiceField(choices=ACTIONS, coerce=int)
    test_recipient = forms.EmailField(
        help_text='If "send test" is selected, send to this recipient instead', required=False)
    mark_as_sent = forms.TypedChoiceField(choices=((None, '(Nothing)'),) + models.NeedToSend.THINGS_TO_SEND,
                                          coerce=int, required=False, initial=None, empty_value=None, help_text='Mark this as sent by the email')
    only_if_unsent = forms.TypedChoiceField(choices=((True, 'Only send if we can mark a thing as sent'), (False, 'Send even if nothing will be marked as sent')),
                                            coerce=bool, required=True, initial=True, help_text="Only send if there's an unsent thing to mark as sent")

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data["action"] == DoMailoutForm.ACTION_SEND_TEST and "test_recipient" in cleaned_data and cleaned_data["test_recipient"] == "":
            self.add_error("test_recipient",
                           "Recipient required for test emails")
        return cleaned_data


class AddDetailsSectionForm(forms.Form):
    groups = forms.ModelMultipleChoiceField(queryset=models.Group.objects)
    details_sections = forms.ModelMultipleChoiceField(
        queryset=models.DetailsSection.objects)
