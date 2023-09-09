from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


from . import views


urlpatterns = [
	
	path('', views.CreationPage, name = 'creation-page'),

	path('signup', views.SignupPage, name = 'signup-page'),

	path('verify/<str:pk>', views.Verify , name = 'verify'),

	path('success', views.VerificationSuccessful, name = 'verification-successful'),

	path('login', views.LoginPage, name = 'login-page'),

	path('home', views.HomePage, name = 'home-page'),

	path('forget_password', views.ForgetPassword, name = 'forget-password'),

	path('change_password/<str:pk>', views.ChangePassword, name = 'change-password'),

	path('activate/<str:pk>', views.ActivateAccount, name = 'activate-account'),

	path('logout', views.Logout, name = 'logout'),

	path('friend', views.Friends, name = 'friend-page'),

	path('friend/986abfdfv74356607<str:pk>742343jfnhdfm480941', views.ViewFriend, name = 'view-friend'),

	path('change-username', views.ChangeUsername, name = 'change-username'),

	path('new-password', views.NewPassword, name = 'new-password'),

	path('change-phonenumber', views.ChangePhonenumber, name = 'change-phonenumber'),

	path('change-email', views.ChangeEmail, name = 'change-email'),

	path('friends', views.MyFriends, name = 'my-friends'),

	path('allfriendsrequest', views.ViewFriendsRequest, name = 'all-friends-request'),

	path('profile-pic', views.ProfilePicture, name = 'profile-picture'),

	path('send-request/kwjdr42725y8<str:pk>uwehy982882b11nbjm', views.SendRequest, name = 'send_request'),
	
	path('accept-request/<str:pk>', views.acceptRequest, name = 'accept'),

	path('delete-request/<str:pk>', views.deleteRequest, name = 'delete'),

	path('chats', views.MyChats, name = 'chats'),

	path('chat/bafdfih468543<str:pk>8u575wqcvmlh5y', views.ChatRoom, name = 'chat-room'),

	path('chat/<str:pk>/edit', views.editChatMessage, name = 'edit-chatmessage'),

	path('chat/<str:pk>/delete', views.deleteChatMessage, name = 'delete-chatmessage'),

	path('group', views.MyGroup, name = 'group-page'),

	path('create-group', views.CreateGroup, name = 'create-group'),

	path('group/<str:name>', views.GroupRoom, name = 'group-room'),

	path('group/<str:pk>/edit', views.editGroupMessage, name = 'edit-group-message'),

	path('group/<str:pk>/picture', views.editGroupPicture, name = 'edit-group-picture'),	

	path('group/<str:pk>/delete', views.deleteGroupMessage, name = 'delete-group-message'),	

	path('group/<str:name>/details', views.GroupInfo, name = 'group-info'),

	path('delete-group/<str:name>', views.deleteGroup, name = 'delete-group'),

	path('group/<str:name>/<str:pk>', views.leaveGroup, name = 'leave-group'),

	path('group/<str:name>/details/edit', views.editGroup, name = 'edit-group-info'),

	path('create_post', views.createPost, name = 'create-post'),

	path('like-post/<str:pk>', views.likePost, name = 'like_post'),

	path('unlike-post/<str:pk>', views.unlikePost, name = 'unlike_post'),

	path('home/<str:pk>', views.PostComment, name = 'comment'),

	path('home/<str:pk>/edit-comment', views.editComment, name = 'edit-comment'),

	path('home/<str:pk>/delete-comment', views.deleteComment, name = 'delete-comment'),

	path('home/<str:pk>/edit-post', views.editPost, name = 'edit-post'),

	path('home/<str:pk>/delete-post', views.deletePost, name = 'delete-post'),

	path('home/<str:pk>/all_comment', views.ViewComments, name = 'viewcomment'),

	path('feedback', views.Feedback, name = 'feedback'),

	path('block_friend/<str:pk>', views.blockFriend, name = 'block_friend'),

	path('unblock_friend/<str:pk>', views.unblockFriend, name = 'unblock_friend'),

	path('unblock_comment/<str:pk>', views.unblockComment, name = 'unblock_comment'),

	path('block_comment/<str:pk>', views.blockComment, name = 'block_comment'),





	# path('verification-page/<str:pk>', views.VerificationPage, name = 'verification-page'),


	]+static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)