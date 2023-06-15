from django.db import models
from django.contrib.auth.models import User 
# Create your models here.


class UserContact(models.Model):
	user = models.OneToOneField(User, on_delete = models.CASCADE, blank = True)
	phone_number = models.CharField('phone number', max_length = 13)
	email_otp = models.CharField('email otp', max_length = 6, blank = True)
	phone_number_otp = models.CharField('phone number otp', max_length = 6, blank = True)
	verify = models.BooleanField(default = False)
	is_online = models.BooleanField(default = False)
	picture = models.ImageField(default = 'user.png', upload_to = 'images/')


	def __str__(self):
		return str(self.user.username)# + ' account detail'

class Message(models.Model):
	sender = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'sender')
	receiver = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'receiver')
	text = models.TextField()
	date = models.DateTimeField(auto_now_add = True)

	def __str__(self):
		return str(self.sender) + ' messsage to ' + str(self.receiver)

		
class Friend(models.Model):
	request_sender = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'request_sender')
	request_receiver = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'request_receiver')
	accept = models.BooleanField(default = False)
	time = models.DateTimeField(auto_now = True)
	message = models.ManyToManyField(Message)
	# request_sender_pic = models.ForeignKey(UserContact, on_delete = models.SET_NULL, null = True, related_name = 'request_sender_pic')
	# request_receiver_pic = models.ForeignKey(UserContact, on_delete = models.SET_NULL, null = True,related_name = 'request_receiver_pic')
	def __str__(self):
		return str(self.request_sender) + ' to ' + str(self.request_receiver)

class GroupMessage(models.Model):
	# group = models.ForeignKey(Group, on_delete = models.CASCADE)
	sender = models.ForeignKey(User, on_delete = models.CASCADE)
	# receiver = models.ManyToManyField(User, related_name = 'group message receiver')
	text = models.TextField()
	time = models.DateTimeField(auto_now_add = True)

	def __str__(self):
		return self.text 

class Group(models.Model):
	name = models.CharField(max_length = 100)
	desc = models.CharField(max_length = 500)
	admin = models.ForeignKey(User, on_delete = models.SET_NULL, blank = True, null = True)
	participant = models.ManyToManyField(User, related_name = 'participant')
	# block_participant = models.BooleanField(default = False)
	group_message = models.ManyToManyField(GroupMessage)
	time = models.DateTimeField(auto_now = True)
	remove = models.BooleanField(default = False)
	group_picture = models.ImageField(default ='', upload_to = 'group_picture/')

	def __str__(self):
		return self.name

	def admin_leave_group(self):
		if self.admin is None:
			return self.participant


class Comment(models.Model):
	text = models.TextField()
	user = models.ForeignKey(User, on_delete = models.CASCADE)
	remove = models.BooleanField(default = False)
	# date = models.DateTimeField(auto_now_add = True)
	def __str__(self):
		return self.text

class Post(models.Model):
	post_creator = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'post_creator')
	content = models.TextField()
	time = models.DateTimeField(auto_now_add = True)
	like = models.ManyToManyField(User)
	comment = models.ManyToManyField(Comment)
	remove = models.BooleanField(default = False)
	post_img = models.ImageField(default = '', upload_to = 'post_image/')
	def __str__(self):
		return self.content




		

