from . import models, staff_views as views
from django.urls import path

urlpatterns = [
    path('mailout/<int:mailout_id>', views.mailout, name='mailout'),
    path('invitations/<int:event_id>',
         views.InviteesView.as_view(), name='invitations'),
    path('attendees/<int:event_id>',
         views.AttendeesView.as_view(), name='attendees'),
    path(
        'thanks/',
        views.NeedToSendView.as_view(what=models.NeedToSend.THANKYOU_CARD),
        name=views.NeedToSendView.view_name_for_type(
            models.NeedToSend.THANKYOU_CARD)
    ),
    path(
        'invitations/',
        views.NeedToSendView.as_view(what=models.NeedToSend.INVITATION),
        name=views.NeedToSendView.view_name_for_type(
            models.NeedToSend.INVITATION)
    ),
    path(
        'save-the-date/',
        views.NeedToSendView.as_view(what=models.NeedToSend.SAVE_THE_DATE),
        name=views.NeedToSendView.view_name_for_type(
            models.NeedToSend.SAVE_THE_DATE)
    ),
    path('mark-as-sent/', views.mark_as_sent, name='mark_as_sent'),
    path('add-details-section/', views.AddDetailsSectionView.as_view(),
         name='add_details_section')
]
