from django.urls import path, include
from tasks.views import BoardAction,CardAction, ColumnsAction, AssigneeDeleteion, CardDeletion,CommentAction, GetComments 
from tasks.views import CardEditUpdate,AddAssignee, CreateMeeting, MeetingAction, DeleteBoard, DeleteMeeting

urlpatterns = [
    path('board/', BoardAction.as_view(), name='create_get_board'),
    path('board/delete/<str:id>/', DeleteBoard.as_view(), name='delete_board'),
    path('board/columns/', ColumnsAction.as_view(), name='create_get_columns'),
    
    path('card/', CardAction.as_view(), name='create_get_card'),
    path('card/comment/', GetComments.as_view(), name="get_comments"),
    path('card/comment/<str:id>/', CommentAction.as_view(), name="comment_action"),
  

    path('card/assignee/<int:id>/', AssigneeDeleteion.as_view(), name='delete_card_assignee'),
    path('card/assignee/invite/', AddAssignee.as_view(), name="add_card_assignee"),
    path('card/delete/<int:id>/', CardDeletion.as_view(), name="delete_card"),
    path('card/card-update/', CardEditUpdate.as_view(), name="edit_card_update"),
   
    path('meeting/create-meeting/', CreateMeeting.as_view(), name="create_meeting"),
    path('meeting/', MeetingAction.as_view(), name='meeting_actions'),
    path('meeting/delete/<str:id>/', DeleteMeeting.as_view(), name="delete_meeting_actions"),
   
   
   
]
