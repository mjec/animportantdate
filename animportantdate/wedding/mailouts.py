from . import models
from . import fields

from collections import namedtuple
from django.conf import settings
from django.core import mail
from django.template import Context, Template  # TODO: use other engines?
from email.mime.image import MIMEImage

MessageBase = namedtuple(
    'MessageBase',
    ("subject", "plain_body", "html_body", "from_", "recipient", "bcc", "open_key"),
)


class Message(MessageBase):
    pass


class MailoutHelper(object):

    def __init__(self, mailout, recipients, override_recipient=None, attach_images=True):
        self.override_recipient = override_recipient
        self._mailout = mailout
        self._recipients = recipients
        self.image_attachments = []
        self.attach_images = attach_images
        if attach_images and mailout.html_body != "":
            for img in mailout.images.all():
                mime_image = MIMEImage(img.file.read())
                mime_image.add_header('Content-ID', '<{}>'.format(img.slug))
                self.image_attachments.append(mime_image)
        self._render_messages()

    @property
    def messages(self):
        return list(self._messages)

    def _render_messages(self):
        messages = []

        for recipient in self._recipients:
            messages.append(self._render_single_message(recipient))

        self._messages = messages

    def send_messages(self):
        try:
            sent = []
            with mail.get_connection() as connection:
                for message in self.messages:
                    send_to = '"{}" <{}>'.format(message.recipient.name, message.recipient.email)
                    headers = {}
                    if self.override_recipient is not None:
                        send_to = self.override_recipient
                        headers['X-Would-Be-To'] = message.recipient.email
                    email_message = mail.EmailMultiAlternatives(
                        message.subject,
                        message.plain_body,
                        message.from_,
                        [send_to],
                        message.bcc,
                        connection,
                        None,
                        headers
                    )
                    if message.html_body != "":
                        email_message.attach_alternative(message.html_body, "text/html")
                        email_message.mixed_subtype = 'related'
                        for image in self.image_attachments:
                            email_message.attach(image)

                    email_message.send()
                    if self.override_recipient is None:
                        sent.append(models.MailSent(
                            mailout=self._mailout,
                            recipient=message.recipient,
                            open_key=message.open_key
                        ))
        finally:
            models.MailSent.objects.bulk_create(sent)


    def _render_single_message(self, recipient):
        open_key = fields.PnrField.generate(6)

        subject_t = Template(self._mailout.subject)
        plain_t = Template(self._mailout.plain_body)
        html_t = Template(self._mailout.html_body)
        context = Context({
            "recipient": recipient,
            "open_key": open_key,
            "mailout": self._mailout,
            "attach_images": self.attach_images,
        })

        subject = subject_t.render(context)
        plain_body = plain_t.render(context)
        html_body = html_t.render(context)
        recipient = recipient
        from_ = models.SiteConfiguration.get_solo().mailouts_from
        if models.SiteConfiguration.get_solo().mailouts_bcc is not None:
            bcc = [models.SiteConfiguration.get_solo().mailouts_bcc]
        else:
            bcc = []

        return Message(subject, plain_body, html_body, from_, recipient, bcc, open_key)
