from django import template
from wedding import models

register = template.Library()

@register.simple_tag(takes_context=True)
def image_src(context, slug, image_attached=None, mailout_name_in_context='mailout'):
    # We could just reutrn 'cid:{slug}' but this way we validate that the image really exists
    if mailout_name_in_context not in context:
        raise template.base.VariableDoesNotExist('The {% mailout_image %} tag requires a mailout to be defined in the context, called {}'.format(mailout_name_in_context))

    try:
        image = models.MailoutImage.objects.get(mailout=context[mailout_name_in_context], slug=slug)
    except models.MailoutImage.DoesNotExist:
        raise template.base.VariableDoesNotExist('There is no image matching the slug "{}" for this mailout'.format(slug))

    if image_attached is None and "attach_images" in context:
        image_attached = context["attach_images"]

    if image_attached:
        return 'cid:{}'.format(image.slug)
    else:
        return image.file.url
