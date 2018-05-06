from django.db import models
from django_countries.fields import CountryField

from solo.models import SingletonModel

from .fields import PnrField

class Group(models.Model):
    ''' A group is an organisation that receives an invitation. '''

    def __str__(self):
        return self.display_name

    def invited(self):
        return 0 if self.events.count() == 0 else self.person_set.count()
    
    def attending(self):
        return 0 if self.events.count() == 0 else self.person_set.filter(rsvp_status=Person.RSVP_ATTENDING).count()
    
    def declined(self):
        return 0 if self.events.count() == 0 else self.person_set.filter(rsvp_status=Person.RSVP_NOT_ATTENDING).count()

    def no_response(self):
        return 0 if self.events.count() == 0 else self.person_set.filter(rsvp_status=Person.RSVP_UNKNOWN).count()

    def add_note(self, content):
        self.notes.create(content=content)

    address_fields = ('address_1', 'address_2', 'address_city', 'address_state_province', 'address_postal_code', 'address_country')

    @classmethod
    def contains_address_field(cls, field_list):
        for f in cls.address_fields:
            if f in field_list:
                return True
        return False

    pnr = PnrField(
        max_length=6,
        unique=True,
        verbose_name="Confirmation Code",
    )

    address_1 = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Address Line 1",
    )
    address_2 = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Address Line 2",
    )
    address_city = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="City/Suburb",
    )
    address_state_province = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="State/Province",
    )
    address_postal_code = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Postal Code",
    )
    address_country = CountryField(
        blank=True,
        verbose_name="Country"
    )
    telephone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name = "Phone number"
    )

    display_name = models.CharField(max_length=255)
    events = models.ManyToManyField(
        "Event",
        blank=True,
        related_name="groups",
    )


class Person(models.Model):

    def __str__(self):
        return self.name

    RSVP_UNKNOWN = 1
    RSVP_ATTENDING = 2
    RSVP_NOT_ATTENDING = 3

    RSVP_CHOICES = (
        (RSVP_UNKNOWN, "No Response"),
        (RSVP_ATTENDING, "Attending"),
        (RSVP_NOT_ATTENDING, "Not attending"),
    )

    name = models.CharField(max_length=255, null=True)
    email = models.EmailField(null=True, blank=True)
    group = models.ForeignKey(Group)
    rsvp_status = models.IntegerField(
        choices=RSVP_CHOICES,
        default=RSVP_UNKNOWN,
    )
    dietary_restrictions = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "people"

class Event(models.Model):

    def __str__(self):
        return self.name
    
    def invited(self):
        return Person.objects.filter(group__events=self.pk).count()
    
    def attending(self):
        return Person.objects.filter(rsvp_status=Person.RSVP_ATTENDING, group__events=self.pk).count()
    
    def declined(self):
        return Person.objects.filter(rsvp_status=Person.RSVP_NOT_ATTENDING, group__events=self.pk).count()

    def no_response(self):
        return Person.objects.filter(rsvp_status=Person.RSVP_UNKNOWN, group__events=self.pk).count()

    short_name = models.CharField(
        max_length=20,
        help_text="This is used to look up an event, e.g. by the "
                  "group_has_event tag.",
        unique=True,
    )
    name = models.CharField(
        max_length=255,
        unique=True,
    )
    date_time = models.DateTimeField()
    end_date_time = models.DateTimeField()
    venue = models.CharField(max_length=255)
    address = models.TextField()
    directions_url = models.CharField(max_length=255)
    description = models.TextField()


class Mailout(models.Model):

    def __str__(self):
        return self.name

    def sent_to(self):
        return self.mailsent_set.count()
        
    def opened_by(self):
        return self.mailsent_set.filter(last_opened__isnull=False).count()

    name = models.CharField(max_length=255)
    event = models.ForeignKey(Event)
    subject = models.CharField(max_length=255)
    plain_body = models.TextField()
    html_body = models.TextField(blank=True)


class MailoutImage(models.Model):
    slug = models.SlugField()
    file = models.ImageField()
    mailout = models.ForeignKey(Mailout, related_name='images')
    
    def __str__(self):
        return '{} for {}'.format(self.slug, self.mailout)

    class Meta:
        unique_together = (('slug', 'mailout'), )

class MailSent(models.Model):
    
    class Meta:
        verbose_name_plural = 'Mails sent'

    def __str__(self):
        if self.last_opened is not None:
            return "{} sent to {} opened {}".format(self.mailout, self.recipient, self.last_opened)
        return "{} sent to {} not yet opened".format(self.mailout, self.recipient)

    recipient = models.ForeignKey(Person)
    mailout = models.ForeignKey(Mailout)
    datestamp = models.DateTimeField(auto_now_add=True)
    last_opened = models.DateTimeField(null=True)
    open_key = PnrField(max_length=6, unique=True)


class NeedToSend(models.Model):
    def __str__(self):
        return 'Need to send {} to {} ({})'.format(
            [e[1] for e in NeedToSend.THINGS_TO_SEND if e[0] == self.what][0] or self.what,
            self.who,
            'outstanding' if self.sent is None else 'done')

    INVITATION = 1
    THANKYOU_CARD = 2

    THINGS_TO_SEND = (
        (INVITATION, "Invitation"),
        (THANKYOU_CARD, "Thank you card"),
    )
    
    who = models.ForeignKey(Group)
    what = models.IntegerField(choices=THINGS_TO_SEND)
    why = models.TextField()
    added = models.DateField(auto_now_add=True)
    sent = models.DateField(default=None, null=True, blank=True)
    sent_note = models.TextField(blank=True)


class Note(models.Model):
    def __str__(self):
        return self.content

    about = models.ForeignKey(Group, related_name='notes')
    created = models.DateTimeField(auto_now_add=True)
    content = models.TextField()


class SiteConfiguration(SingletonModel):
    mailouts_from_name = models.CharField(max_length=60)
    mailouts_from_email = models.EmailField()
    mailouts_bcc = models.EmailField(blank=True, null=True, default=None)
    physical_address = models.TextField(blank=True)

    @property
    def mailouts_from(self):
        return '"{}" <{}>'.format(self.mailouts_from_name, self.mailouts_from_email)

    def __unicode__(self):
        return u"Site Configuration"

    class Meta:
        verbose_name = "Site Configuration"
