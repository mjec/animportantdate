from django.core import mail


class MailAlert(object):

    def send(self, **k):
        print(self.message(**k))
        mail.mail_managers(self.subject(**k), self.message(**k), True)

    def subject(self, **k):
        return self.__SUBJECT__.format_map(k)

    def message(self, **k):
        return self.__TEMPLATE__.format_map(k)


class GroupContactUpdate(MailAlert):
    __SUBJECT__ = "Group contact details updated - {group.display_name}"
    __TEMPLATE__ = '''Hello!

The following group has has updated their contact information.
Enjoy!

Group: {group.display_name}

RSVPs: {group.rsvp_summary}

Changed information: {fields}

New invitation required: {new_invitation_required}

<3,

--Your wedding app.'''


def group_contact_update(group, fields, new_invitation_required):
    GroupContactUpdate().send(group=group, fields=fields,
                              new_invitation_required=new_invitation_required)
