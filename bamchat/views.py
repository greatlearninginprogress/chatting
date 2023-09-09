from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime
from django.db.models import Q
from django.shortcuts import render, redirect
import random
from .models import UserContact, Friend, Message, Group, GroupMessage, Post, Comment
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
import random
from django.core.mail import send_mail
from django.conf import settings
import smtplib
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


# Create your views here.
alphabet = ['A','B','C','D','E','F','G','H','I','J','K','L',
			'M','N','O','P','Q','R','S','T',
			'U','V','W','X','Y','Z']
def PhoneOTP():
	first_num = random.randrange(10,100)
	second_num = random.randrange(10,100)
	first_alp = random.choice(alphabet)
	second_alp = random.choice(alphabet)
	phone_otp = str(first_alp)+str(first_num)+str(second_alp)+str(second_num)
	return phone_otp

def PhoneNumberOTP(phone_number):
	phone_number_otp = str(random.randrange(1000,10000))
	return phone_number_otp

def CreationPage(request):
	return render(request, 'bamchat/creation-page.html')

def SignupPage(request):

	if request.method == 'POST':
		username = request.POST.get('username').lower()
		email = request.POST.get('email')
		phone_number = request.POST.get('phone_number')
		password = request.POST.get('password')
		cpassword = request.POST.get('cpassword')
		
		if len(password) >= 8:
			if password == cpassword:
				if len(phone_number) < 11 or len(phone_number) > 13:
					print(len(phone_number))
					
					messages.error(request, 'Invalid phone number')

				elif email[-4:] != '.com':
					
					messages.error(request, 'Invalid email')

				elif len(username) < 3:
					
					messages.error(request, 'Username should be minimum of 3 characters')

				elif User.objects.filter(email = email).exists():
					messages.error(request, 'Account with this email already exist')

				elif User.objects.filter(username = username).exists():
					messages.error(request, 'Account with this username already exist')

				elif UserContact.objects.filter(phone_number = str(phone_number)).exists():
					messages.error(request, 'Account with this phone number already exist')
										
				else:
					user = User.objects.create_user(email = email, username = username, password = password)

					user_contact = UserContact.objects.create(user = user,
													  		  phone_number = phone_number,
													  		  phone_number_otp = PhoneOTP())


					user_contact = UserContact.objects.get(user = user)
					subject = 'BAMCHAT ACCOUNT ACTIVATION'
					message = 'Welcome '+str(username.upper())+'. Your OTP is '+ str(user_contact.phone_number_otp)
					from_email = settings.EMAIL_HOST_USER
					recipient_list = [email]
					# print(subject)
					# print(message)
					# print(from_email)
					# print(recipient_list)
					# s = smtplib.SMTP('smtp.gmail.com', 587)
					# s.starttls()
					# s.login('bamchat99@gmail.com','bamchat99-08031999')
					# s.sendmail('bamchat99@gmail.com',email,message)
					# s.quit()
					# send_mail(subject,message,settings.EMAIL_HOST_USER,	recipient_list)#, fail_silently=False)
					html_content = render_to_string('bamchat/email_template.html',{'user':user_contact.user.username.title(),
					 'otp':user_contact.phone_number_otp})
					text_content = strip_tags(html_content)
					html_email = EmailMultiAlternatives(subject,text_content,from_email, recipient_list)
					html_email.attach_alternative(html_content,"text/html")
					html_email.send()



					return redirect('verify', pk = user_contact.id)

			else:
				messages.error(request, 'Password not match')
			
			
		else:
			messages.error(request, 'Password not strong enough, use atleast 8 characters')
			
				
	try:
		context = { 
				'username':username, 
				'email':email,
				'password':password, 
				'cpassword':cpassword, 
				'phone_number':phone_number}
	except:
		context = {}

	return render(request, 'bamchat/signup-page.html', context)

def Verify(request, pk):
	try:
		user_contact = UserContact.objects.get(id = pk)
		user = User.objects.get(id = user_contact.user.id)
		email = user.email
		context = {'email':email}
	except:
		context = {}

	if request.method == 'POST':
		phone_number_otp = request.POST.get('phone_number_otp')
		if str(user_contact.phone_number_otp) == str(phone_number_otp):
			user_contact.verify = True
			user_contact.save()
			return redirect('verification-successful')
		else:
			messages.error(request, 'You entered wrong OTP, please re-check the OTP sent to you')	
	

	return render(request, 'bamchat/verification.html', context)



def ActivateAccount(request, pk):
	user_contact = UserContact.objects.get(id = pk)
	user  = User.objects.get(id = user_contact.user.id)
	email = user.email
	context = {'email': email,
				'pk': pk
				}
	if request.method == 'POST':
		otp = request.POST.get('otp')
		context = {'email': email,
				'pk': pk,
				'otp':otp
				}
		if user_contact.phone_number_otp == otp:
			user_contact.verify = True
			print('yes')
			user_contact.save()
			return redirect('verification-successful')
		else:
			messages.error(request, 'You input wrong OTP')

	return render(request, 'bamchat/activate-account.html', context)


def VerificationSuccessful(request):
	return render(request, 'bamchat/verification_success.html')

def LoginPage(request):
	context = {}
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		at = '@'
		context = {
					'username':username,
					'password':password,
					'error':'error'
					
					}
		if at in username:
			if User.objects.filter(email__iexact = username).exists():
				user = User.objects.get(email__iexact = username)
				user_contact = UserContact.objects.get(user = user)
				if user_contact.verify == True:
					USER = authenticate(username = user.username, password = password)
					if USER is not None:
						login(request, USER)
						user_contact.is_online = True
						user_contact.save()
						return redirect('home-page')
					else:messages.error(request, 'invalid credentials')
				else:
					user_contact.phone_number_otp = PhoneOTP()
					user_contact.save()
					subject = 'BAMCHAT ACCOUNT ACTIVATION'
					from_email =  settings.EMAIL_HOST_USER
					recipient_list = [user_contact.user.email]
					html_content = render_to_string('bamchat/email_template.html',{'user':user_contact.user.username.title(),
					 'otp':user_contact.phone_number_otp})
					text_content = strip_tags(html_content)
					html_email = EmailMultiAlternatives(subject,text_content,from_email, recipient_list)
					html_email.attach_alternative(html_content,"text/html")
					html_email.send()
					# print(user_contact.phone_number_otp)

					return redirect ('activate-account', pk = user_contact.id)
			else:
				messages.error(request, 'Enter valid email')
		else:
			if UserContact.objects.filter(phone_number__iexact = username).exists():
				user_contact = UserContact.objects.get(phone_number = username)
				if user_contact.verify == True:
					USERNAME = user_contact.user.username
					USER = authenticate(username = USERNAME, password = password)
					if USER is not None:
						login(request, USER)
						user_contact.is_online = True
						user_contact.save()
						return redirect('home-page')
					else:messages.error(request, 'invalid credentials')

				else:
					user_contact.phone_number_otp = PhoneOTP()
					user_contact.save()
					subject = 'BAMCHAT ACCOUNT ACTIVATION'
					from_email =  settings.EMAIL_HOST_USER
					recipient_list = [user_contact.user.email]
					html_content = render_to_string('bamchat/email_template.html',{'user':user_contact.user.username.title(),
					 'otp':user_contact.phone_number_otp})
					text_content = strip_tags(html_content)
					html_email = EmailMultiAlternatives(subject,text_content,from_email, recipient_list)
					html_email.attach_alternative(html_content,"text/html")
					html_email.send()
					return redirect ('activate-account', pk = user_contact.id)
			else:
				messages.error(request, 'Enter valid phone number or email')


	return render (request, 'bamchat/login.html', context)


# def VerificationPage(request, pk):
# 	user_contact = UserContact.objects.get(id = pk)
# 	context = {'user_contact':user_contact}
# 	return render(request, 'bamchat/verification-page.html', context)


@login_required(login_url = 'login-page')
def HomePage(request):
	request.session.set_expiry(0)
	pst = []
	fnd = []
	all_post = []
	user = request.user
	try:
		user_contact = UserContact.objects.get(user = user.id)
	except:
		user_contact = None

	if Post.objects.filter(post_creator = request.user).exists():
		post = Post.objects.filter(post_creator = request.user).distinct().order_by('-time')
		for p in post:
			pst.append(p.id)


	if Friend.objects.filter(Q(request_sender = request.user, accept = True)| 
			Q(request_receiver = request.user, accept = True)).exists():
		friends = Friend.objects.filter(Q(request_sender = request.user, accept = True)| 
			Q(request_receiver = request.user, accept = True))

		for friend in friends:
			if friend.request_receiver == request.user:
				fnd.append(friend.request_sender)
			else:
				fnd.append(friend.request_receiver)

		if fnd is not None:

			for f in fnd:
				if Post.objects.filter(post_creator = f).exists():
					PST = Post.objects.filter(post_creator = f).distinct().order_by('-time')
					for i in PST:
						pst.append(i.id)
	# random.shuffle(pst)
	pst.sort()
	pst.reverse()
	# print(pst)
	for i in pst:
		p = Post.objects.get(id = i)
		all_post.append(p)
	context = {
					'user':request.user,
					'posts':all_post

					}
	


	return render (request, 'bamchat/home.html',context)


def ForgetPassword(request):
	context = {}
	if request.method == 'POST':
		email = request.POST.get('email')
		if User.objects.filter(email = email).exists():
			user = User.objects.get(email = email )
			user_contact = UserContact.objects.get(user = user)
			user_contact.phone_number_otp = PhoneOTP()
			user_contact.save()
			subject = "BAMCHAT PASSWORD RESET"
			from_email = settings.EMAIL_HOST_USER
			recipient_list = [email]
			# send_mail(
			# 			subject = 'Bamchat OTP Verification',
			# 			message = 'Your OTP is '+ str(user_contact.phone_number_otp),
			# 			from_email = settings.EMAIL_HOST_USER,
			# 			recipient_list = [email]
			# 			)
			html_content = render_to_string('bamchat/reset_password_email_template.html',{'user':user_contact.user.username.title(),
					 'otp':user_contact.phone_number_otp})
			text_content = strip_tags(html_content)
			html_email = EmailMultiAlternatives(subject,text_content,from_email, recipient_list)
			html_email.attach_alternative(html_content,"text/html")
			html_email.send()
			# reset_password_email_template.html
			return redirect('change-password', pk = user.id )
		else:
			context = {'email':email}
	return render(request, 'bamchat/forget-password.html', context)


def ChangePassword(request, pk):
	user = User.objects.get(id = pk )
	user_contact = UserContact.objects.get(user = user)
	phone_number = user_contact.phone_number[-4:]
	context = {
				'phone_number':phone_number,
				'email': user.email
				}
	if request.method == 'POST':
		otp = request.POST.get('otp')
		password = request.POST.get('password')
		cpassword = request.POST.get('cpassword')
		context = {
					'otp':otp,
					'password':password,
					'cpassword':cpassword,
					'phone_number':phone_number,
					'email':user.email
					}
		if user_contact.phone_number_otp == otp :
			if len(password) >= 8:
				if password == cpassword:
					user.set_password(password)
					user.save()
					messages.success(request, 'Password change successfully')
					return redirect('login-page')
				else:
					messages.error(request, 'Password not match')
			else:
				messages.error(request, 'password not strong')
		else:
			messages.error(request, 'You entered wrong OTP')
	return render(request, 'bamchat/change-password.html', context)

	
def Logout(request):
	# user = request.user
	# USER = User.objects.get(id = user.id)
	user_contact = UserContact.objects.get(user = request.user)
	auth.logout(request)
	user_contact.is_online = False
	user_contact.save()
	return redirect('login-page')

@login_required(login_url = 'login-page')
def acceptRequest(request, pk):
	request.session.set_expiry(0)
	friend = Friend.objects.get(id = pk)
	friend.accept = True
	friend.save()
	return redirect('friend-page')
	
@login_required(login_url = 'login-page')
def deleteRequest(request, pk):
	request.session.set_expiry(0)
	friend = Friend.objects.get(id = pk)
	friend.delete()
	return redirect('friend-page')


@login_required(login_url = 'login-page')
def Friends(request):
	request.session.set_expiry(0)
	my_request = Friend.objects.filter(request_sender = request.user, accept = False).order_by('-id')
	friend_request = Friend.objects.filter(request_receiver = request.user, accept = False).order_by('-id')
	

	context = {'my_request':my_request[:2],
			   'my_req_length':len(my_request),

			   'frnd_req_length':len(friend_request),
			   'friend_request':friend_request[:2]
	}
	if request.method == 'POST':
		friend = request.POST.get('friend')
		# print(friend)
		if friend != '':
			friends = UserContact.objects.filter(Q(phone_number__icontains = friend, verify = True)|
				Q(user__username__icontains = friend, verify = True))
			

			context = {'friends':friends,

						}
			return render(request, 'bamchat/search_result.html', context)


	return render(request, 'bamchat/friends.html', context)

@login_required(login_url = 'login-page')
def ViewFriendsRequest(request):
	request.session.set_expiry(0)
	friend_request = Friend.objects.filter(request_receiver = request.user, accept = False).order_by('-id')

	context = {'friend_requests':friend_request}
	return render(request,'bamchat/all_friends_request.html', context)

@login_required(login_url = 'login-page')
def ViewFriend(request, pk):
	request.session.set_expiry(0)
	user = User.objects.get(id = pk)
	try:

		fnd = Friend.objects.get(
			Q(request_sender = request.user, request_receiver = user)|
			Q( request_sender = user, request_receiver = request.user)
			)
	except:
		fnd = 'Add Friend'
	
	friend = str(user.id) + '&' +str(request.user.id)
	print(friend)
	context = {'username':user.username,
				'USER':user,
				'f':friend,
				'fnd':fnd,
				't':True,
				'false':False
				
				}
	return render(request, 'bamchat/view_friend.html', context)
# def DeleteRequest(request):

@login_required(login_url = 'login-page')
def SendRequest(request, pk):
	request.session.set_expiry(0)
	arg = pk.split('&')
	login_user_id = arg[1]
	request_to_id =  arg[0]
	
	login_user = User.objects.get(id = login_user_id)
	request_to = User.objects.get(id = request_to_id)
	print('login_user : ', login_user)
	print('request_to : ', request_to)
	friend = Friend(request_sender = login_user , request_receiver = request_to)
	friend.save()
	return redirect('view-friend', pk = request_to_id)


@login_required(login_url = 'login-page')
def ChangeUsername(request):
	request.session.set_expiry(0)
	context = {}
	if request.method == 'POST':
		username = request.POST.get('username').lower()
		context = {'username':username}
		if len(username) < 3:
			messages.error(request, 'username should contain atleast 3 character')
		else:
			if User.objects.filter(username__iexact = username).exists():
				messages.error(request, 'username already exist')
			else:
				user = request.user
				# print(user.id, user.username)
				USER = User.objects.get(id = user.id)
				USER.username = username
				USER.save()
				return redirect('home-page')
			# print(user.id, user.username)
	return render(request, 'bamchat/change-username.html', context)

@login_required(login_url = 'login-page')
def NewPassword(request):
	request.session.set_expiry(0)
	context = {}
	if request.method == 'POST':
		password = request.POST.get('password')
		cpassword = request.POST.get('cpassword')
		if len(password) < 8:
			context = {'password':password,
						'cpassword':cpassword
						}
			messages.error(request, 'password not strong enough, password must be atleast 8 characters')
		else:
			if password != cpassword:
				context = {'password':password,
						'cpassword':cpassword
						}
				messages.error(request, 'password does not match confirm password ')

			else:
				user = request.user 
				# print(user.id)
				USER = User.objects.get(id = user.id)
				USER.set_password(password)
				USER.save()
				return redirect('home-page')


	return render(request, 'bamchat/password-change.html', context)


@login_required(login_url = 'login-page')
def ChangePhonenumber(request):
	request.session.set_expiry(0)
	context = {}
	if request.method == 'POST':
		phone_number = request.POST.get('phone_number')
		context = {'phone_number':phone_number}
		# print(phone_number)
		# check = UserContact.objects.get(user = request.user)
		# if check.phone_number == phone_number:
		# 	pass
		if UserContact.objects.filter(phone_number = phone_number).exclude(user = request.user).exists():
			messages.error(request, 'phone number already used')
		else:
			user = request.user 
			user_contact = UserContact.objects.get(user = user)
			user_contact.phone_number = phone_number
			user_contact.save()
			return redirect('home-page')
				
	return render(request, 'bamchat/change-phonenumber.html', context)

@login_required(login_url = 'login-page')
def MyFriends(request):
	request.session.set_expiry(0)
	fnd = Friend.objects.filter(
			Q(request_sender = request.user, accept = True)|
			Q(request_receiver = request.user, accept = True)
		)

	context = {"friends":fnd,
				"length":fnd.count()
			}
	
	return render(request, 'bamchat/myfriends.html', context)


@login_required(login_url = 'login-page')
def ProfilePicture(request):
	request.session.set_expiry(0)
	if request.method == 'POST':
		picture = request.FILES.get('picture')
		if picture:
			extension = picture.name.split('.')[-1]
			user_contact = UserContact.objects.get(user = request.user) 
			if extension.lower() =='jpg':
				user_contact.picture = picture
				user_contact.save()
				return redirect('home-page')
			elif extension.lower() == 'png':
				user_contact.picture = picture
				user_contact.save()
				return redirect('home-page')
			elif extension.lower() == 'gif':
				user_contact.picture = picture
				user_contact.save()
				return redirect('home-page')
			else:
				messages.error(request,' Invalid image selected. Please select image type of "jpg","png" or "gif"')
		else:
			messages.error(request,' No image selected. Please select image type of "jpg", png or gif')
		
	return render(request, 'bamchat/profile-pic.html')


@login_required(login_url = 'login-page')
def ChangeEmail(request):
	request.session.set_expiry(0)
	context = {}
	if request.method == 'POST':
		email = request.POST.get('email')
		context = {'email':email}
		if User.objects.filter(email__iexact = email).exists():
			messages.error(request, 'email already exist')
		else:
			user = request.user
			USER = User.objects.get(id = user.id)
			USER.email = email
			USER.save()
			return redirect('home-page')

	return render(request, 'bamchat/change-email.html')

@login_required(login_url = 'login-page')
def MyChats(request):
	request.session.set_expiry(0)
	last_message = []
	friends = list(Friend.objects.filter(Q(request_sender = request.user, accept = True)| 
		Q(request_receiver = request.user, accept = True)).order_by("-time"))
	# print(friends)

	for friend in friends:
		if friend.message.all():
			messages = list(friend.message.all())
			last_message.append(str(messages[-1].text[:8])+'......')
				
		else:
			last_message.append('')

	friend_messages = zip(friends,last_message)

	context = {
					
					'friend_messages':friend_messages
					
					}
		# context = {}
	# print(friend_message)
	if request.method == 'POST':
		fnd = request.POST.get('friend')
		fnds = Friend.objects.filter(

			Q(request_sender__username__icontains = fnd, request_receiver__username = request.user, accept = True)|
			Q(request_sender__username = request.user, request_receiver__username__icontains = fnd, accept = True)|
			Q(request_receiver__usercontact__phone_number__icontains = fnd, request_sender__username = request.user,accept = True)|
			Q(request_sender__usercontact__phone_number__icontains = fnd, request_receiver__username = request.user, accept = True)
			)
		context = {'friends':fnds,
					}
		return render(request, 'bamchat/friend_list.html', context)

	return render(request, 'bamchat/chat.html', context)
@login_required(login_url = 'login-page')
def ChatRoom(request, pk):
	request.session.set_expiry(0)
	user = User.objects.get(id = pk)
	# print(request.user, user)
	# messages = None
	# error = False
	# try:
	if Friend.objects.filter(Q(request_sender = request.user, request_receiver = user)|
		Q(request_receiver = request.user, request_sender = user)).exists():
		messages = Message.objects.filter(Q(sender = request.user, receiver = user)|
				Q(receiver = request.user, sender = user)).order_by("id")
				# error = False
		friend = Friend.objects.get(Q(request_sender = request.user, request_receiver = user)
			|Q(request_receiver = request.user, request_sender = user))
	else:
		return redirect('view-friend', pk = user.id)		
		# 	return HttpResponse('<h1>You are not allowed here</h1>')
		
	# except:
	# 	messages = None
	
	context = {
				'messages':messages,
				'user':user,
				'friend':friend,
				'id':pk
				# 'error':error
				}

	
	
	if request.method == "POST":
		text = request.POST.get('text')
		message = Message.objects.create(sender = request.user, receiver = user, text = text)
		message.save()
		fm = Friend.objects.get(Q(request_sender = request.user, request_receiver = user)|
			Q(request_sender = user, request_receiver = request.user))
		fm.message.add(message)
		fm.save()
		

		return redirect('chat-room',pk = user.id)

	return render(request, 'bamchat/chatroom.html', context)

@login_required(login_url = 'login-page')
def blockFriend(request,pk):
	# request.session.set_expiry(0)
	user = User.objects.get(id = pk)
	fnd = Friend.objects.get(Q(request_sender = request.user, request_receiver = user)
		|Q(request_receiver = request.user, request_sender = user))
	fnd.block = True
	fnd.block_initiator = request.user.username
	fnd.save()
	return redirect('chat-room', pk = pk)

@login_required(login_url = 'login-page')
def unblockFriend(request,pk):
	# request.session.set_expiry(0)
	user = User.objects.get(id = pk)
	fnd = Friend.objects.get(Q(request_sender = request.user, request_receiver = user)
		|Q(request_receiver = request.user, request_sender = user))
	fnd.block = False
	fnd.block_initiator = request.user.username
	fnd.save()
	return redirect('chat-room', pk = pk)

@login_required(login_url = 'login-page')
def editChatMessage(request, pk):
	request.session.set_expiry(0)
	message = Message.objects.get(id = pk)
	if message.sender == request.user:
		if request.method == 'POST':
			message_content = request.POST.get('message_content')
			message.text = message_content
			message.save()
			return redirect('chat-room', pk = message.receiver.id)
	else:
		return HttpResponse('You are not authorized to edit this message')
	context ={"message":message}
	return render(request, 'bamchat/editchatmessage.html', context)

@login_required(login_url = 'login-page')
def deleteChatMessage(request, pk):
	request.session.set_expiry(0)
	message = Message.objects.get(id = pk)
	if message.sender == request.user:
		if request.method == 'POST':
			confirm = request.POST.get('confirm')
			if confirm =='Yes':
				message.delete()
			
				return redirect('chat-room', pk = message.receiver.id)
	else:
		return HttpResponse('You are not authorized to delete this message')
	context = {'delete':True}
	return render(request, 'bamchat/editchatmessage.html', context)


@login_required(login_url = 'login-page')
def MyGroup(request):
	request.session.set_expiry(0)
	
	last_message = []
	groups = list(Group.objects.filter(Q(admin = request.user)|
			Q(participant = request.user)).distinct().order_by('-time'))

	for group in groups:
		if group.group_message.all():
			gm = list(group.group_message.all())
			gm = str(gm[-1].text[:7])+'.....'
			
		# print(last_message)
			# gm = str(gm[-1][:5])+'....'
			last_message.append(gm)
		else:
				# group_list.append(group)
			gm = ''
			last_message.append(gm)
	groups_message = zip(groups,last_message)

	context = {
					'group_message':groups_message
		}
	
	
	return render(request, 'bamchat/group.html', context)


@login_required(login_url = 'login-page')
def CreateGroup(request):
	request.session.set_expiry(0)
	friends = list(Friend.objects.filter(
		Q(request_sender = request.user, accept = True)| 
		Q(request_receiver = request.user, accept = True)))
	context= {}
	if friends:
		context = {
					'friends':friends
		}
	if request.method == 'POST':
		mem_list = []
		member_list = []
		group_name = request.POST.get('group_name')
		group_desc = request.POST.get('group_desc')
		group_picture = request.FILES.get('group_picture')
		if friends:
			for friend in friends:
				if friend.request_sender == request.user:
					# print(friend.request_receiver.id)
					mem = 'member'+str(friend.request_receiver.id)
					mem_list.append(mem)
				elif friend.request_receiver == request.user:
					# print(friend.request_sender.id)
					mem = 'member'+str(friend.request_sender.id)
					mem_list.append(mem)

			# print(mem_list)
			for i in mem_list:
				member = request.POST.get(i)
				if member is not None:
					member_list.append(int(member))
		if group_picture:
			extension = group_picture.name.split('.')[-1]
			if extension.lower() == 'jpg':
				if group_desc != '':
					if Group.objects.filter(name__iexact = group_name).exists():
						messages.error(request, 'Group with this name already exist')
					else:
						group = Group(admin = request.user, name  = group_name, desc = group_desc,
						group_picture = group_picture )
						group.save()
						user_list = []
						for member_id in member_list:
							user = User.objects.get(id = member_id)
							# user_list.append(user)
							group.participant.add(user)
							group.save()
						return redirect('group-page')
				else:
					if Group.objects.filter(name__iexact = group_name).exists():
						messages.error(request, 'Group with this name already exist')
					else:
						group = Group(admin = request.user, name  = group_name )
						group.save()
						user_list = []
						for member_id in member_list:
							user = User.objects.get(id = member_id)
							# user_list.append(user)

							group.participant.add(user)
							group.save()

						return redirect('group-page')
			elif extension.lower() == 'png':
				if group_desc != '':
					if Group.objects.filter(name__iexact = group_name).exists():
						messages.error(request, 'Group with this name already exist')
					else:
						group = Group(admin = request.user, name  = group_name, desc = group_desc,
						group_picture = group_picture )
						group.save()
						user_list = []
						for member_id in member_list:
							user = User.objects.get(id = member_id)
							# user_list.append(user)
							group.participant.add(user)
							group.save()
						return redirect('group-page')
				else:
					if Group.objects.filter(name__iexact = group_name).exists():
						messages.error(request, 'Group with this name already exist')
					else:
						group = Group(admin = request.user, name  = group_name )
						group.save()
						user_list = []
						for member_id in member_list:
							user = User.objects.get(id = member_id)
							# user_list.append(user)

							group.participant.add(user)
							group.save()

						return redirect('group-page')

			elif extension.lower() == 'gif':
				if group_desc != '':
					if Group.objects.filter(name__iexact = group_name).exists():
						messages.error(request, 'Group with this name already exist')
					else:
						group = Group(admin = request.user, name  = group_name, desc = group_desc,
						group_picture = group_picture )
						group.save()
						user_list = []
						for member_id in member_list:
							user = User.objects.get(id = member_id)
							# user_list.append(user)
							group.participant.add(user)
							group.save()
						return redirect('group-page')
				else:
					if Group.objects.filter(name__iexact = group_name).exists():
						messages.error(request, 'Group with this name already exist')
					else:
						group = Group(admin = request.user, name  = group_name )
						group.save()
						user_list = []
						for member_id in member_list:
							user = User.objects.get(id = member_id)
							# user_list.append(user)

							group.participant.add(user)
							group.save()

						return redirect('group-page')
			else:
				messages.error(request, 'Invalid picture type selected. Please select image type of "png", "jpg" or "gif".')
			
		else:
			if group_desc != '':
				if Group.objects.filter(name__iexact = group_name).exists():
					messages.error(request, 'Group with this name already exist')
				else:
					group = Group(admin = request.user, name  = group_name, desc = group_desc )
					group.save()
					user_list = []
					for member_id in member_list:
						user = User.objects.get(id = member_id)
							# user_list.append(user)
						group.participant.add(user)
						group.save()
					return redirect('group-page')
		
	
			else:
				if Group.objects.filter(name__iexact = group_name).exists():
					messages.error(request, 'Group with this name already exist')
				else:
					group = Group(admin = request.user, name  = group_name )
					group.save()
					user_list = []
					for member_id in member_list:
						user = User.objects.get(id = member_id)
						# user_list.append(user)

						group.participant.add(user)
						group.save()

					return redirect('group-page')

		# print(member_list)
	return render(request, 'bamchat/create-group.html', context)

@login_required(login_url = 'login-page')
def editGroupMessage(request,pk):
	request.session.set_expiry(0)
	group_id = pk.split('%')[1]
	message_id = pk.split('%')[0]
	message = GroupMessage.objects.get(id = message_id)
	group = Group.objects.get(id = group_id)
	if message.sender == request.user:
		if request.method == 'POST':
			group_message = request.POST.get('group_message')
			message.text = group_message
			message.save()
			return redirect('group-room', name = group.name)
	else:
		return HttpResponse('You are not authorized to edit this message')
	context = {'message':message}
	return render(request, 'bamchat/editgroupmessage.html', context)


@login_required(login_url = 'login-page')
def deleteGroupMessage(request,pk):
	request.session.set_expiry(0)
	group_id = pk.split('%')[1]
	message_id = pk.split('%')[0]
	message = GroupMessage.objects.get(id = message_id)
	group = Group.objects.get(id = group_id)
	if message.sender == request.user:
		if request.method == 'POST':
			confirm = request.POST.get('confirm')
			if confirm == 'Yes':
				message.delete()
				return redirect('group-room', name = group.name)
	else:
		return HttpResponse('You are not authorized to delete this message')
	context = {'delete':True}
	return render(request, 'bamchat/editgroupmessage.html', context)



@login_required(login_url = 'login-page')
def GroupRoom(request,name):
	request.session.set_expiry(0)
	if Group.objects.filter(Q(name = name, admin = request.user)|Q(name = name, participant = request.user)).exists():
		messages = GroupMessage.objects.filter(group__name__exact = name)
		group = Group.objects.get(name__exact = name)
		message_and_group_id = []
		if messages:
			for message in messages:
				message_and_group_id.append(str(message.id)+'%'+str(group.id))

			messages_and_group_id = zip(message_and_group_id, messages)
			context = {
				'messages':messages,
				'group_name':name,
				"messages_and_group_id":messages_and_group_id
						}
		else:
			context = {
				'messages':None,
				'group_name':name,
						}

	else:
		return HttpResponse('<h1>You are not allowed to view this page</h1>')

	if request.method == 'POST':
		message = request.POST.get('text')
		group = Group.objects.get(name__exact = name)
		gm = GroupMessage.objects.create(sender = request.user, text = message)
		group.group_message.add(gm)
		group.save()
		return redirect('group-room', name = group.name)

	return render(request, 'bamchat/group-room.html', context)

@login_required(login_url = 'login-page')
def GroupInfo(request,name):
	group = Group.objects.get(name__exact = name)
	request.session.set_expiry(0)
	if group.admin == request.user:
		grp = group
	elif request.user in group.participant.all():
		grp = group
	else:
			return HttpResponse('<h1>You are not allowed to view this page </h1')
	context = {
			'group':grp,
			'mem_num': len(list(grp.participant.all())),
			'num_of_participant':len(list(grp.participant.all()))+1,
	}
	if request.method == 'POST':
		number = request.POST.get('number')
		if UserContact.objects.filter(phone_number__exact = number).exists():
			user_contact = UserContact.objects.get(phone_number__exact = number)
			if user_contact.user in group.participant.all():
				messages.error(request,'the user is already a member of this group')
				context = {
					'group':grp,
					'number':number
			}
			elif user_contact.user == group.admin:
				messages.error(request,'the user is already a member of this group')
				context = {
					'group':grp,
					'number':number
			}
			else:
				group.participant.add(user_contact.user)
				group.save()
				return redirect('group-info', name = name)
		else:
			messages.error(request, 'no user found with this number')
			context = {
					'group':grp,
					'number':number
			}
	return render(request, 'bamchat/group-info.html', context)

@login_required(login_url = 'login-page')
def deleteGroup(request, name):
	request.session.set_expiry(0)
	group = Group.objects.get(name__iexact = name)
	# if group.admin == request.user:
	group.delete()
	return redirect('group-page')


@login_required(login_url = 'login-page')
def leaveGroup(request, name, pk):
	request.session.set_expiry(0)
	if User.objects.filter(id = pk).exists():
		group = Group.objects.get(name__iexact = name)
		user = User.objects.get(id = pk)
		if user in group.participant.all():
			group.participant.remove(user)
			group.save()
			return redirect('group-page')
		elif user == group.admin:
			pat = list(group.participant.all())
			if len(pat) < 1:
				group.delete()
				return redirect('group-page')
			else:
				new_admin = random.choice(pat)
				group.admin = new_admin
				group.participant.remove(new_admin)
				group.save()
				return redirect('group-page')
		else:
			return HttpResponse('<p>You are not allowed here</p>')
	else:
		return HttpResponse('not found')

@login_required(login_url = 'login-page' )
def editGroup(request, name):
	request.session.set_expiry(0)
	if Group.objects.filter(name__exact = name).exists():
		group = Group.objects.get(name__exact = name)
		if request.user == group.admin:
			context = {
					'group':group
			}
		elif request.user in group.participant.all():
			context = {
					'group':group
			}
		else:
			return HttpResponse('<h1>You are not a member of this group</h1>')

		if request.method == 'POST':
			name1 = request.POST.get('name')
			desc = request.POST.get('desc')
			pk = request.POST.get('pk')
			if name == name1:
				if desc =='':
					group.name = name1
					group.save()
				
				
				else:
					group.name = name1
					group.desc = desc
					group.save()
				# print('desc',desc)

				return redirect('group-info', name = name1)
			else:
				if Group.objects.filter(name__iexact = name1).exists():
					messages.error(request, 'group with this name already exist')
					return redirect('edit-group-info', name = name)
				else:
					if desc =='':
						group.name = name1
						group.save()
					
					
					else:
						group.name = name1
						group.desc = desc
						group.save()
					print('desc',desc)

					return redirect('group-info', name = name1)

		return render(request, 'bamchat/editgroup-info.html', context)


	
	return HttpResponse('<h1>Group does not exist</h1>')

@login_required(login_url =  'login-page')
def editGroupPicture(request, pk):
	group = Group.objects.get(id = pk)
	if request.user == group.admin:
		if request.method == 'POST':
			group_picture = request.FILES.get('group_picture')
			extension = group_picture.name.split('.')[-1]
			if extension.lower() == 'jpg':
				group.group_picture = group_picture
				group.save()
				return redirect('group-info', name = group.name)
			elif extension.lower() == 'png':
				group.group_picture = group_picture
				group.save()
				return redirect('group-info', name = group.name)
			elif extension.lower() == 'gif':
				group.group_picture = group_picture
				group.save()
				return redirect('group-info', name = group.name)
			else:
				messages.error(request, 'Invalid image type. Please select image type of "jpg", "png" or "gif".')

	else:
		return HttpResponse('You are not authorized to do this')
	context = {'picture':True, 'group':group}
	return render(request, 'bamchat/editgroup-info.html', context)


@login_required(login_url =  'login-page')
def createPost(request):
	request.session.set_expiry(0)
	
	if request.method == 'POST':
		content = request.POST.get('post_content')
		image = request.FILES.get('image')

		if image:
			extension = image.name.split('.')[-1]
			if extension.lower() == 'jpg':
				post = Post(content = content, post_creator = request.user, post_img = image)
				post.save()
				return redirect('home-page')
			elif extension.lower() == 'png':
				post = Post(content = content, post_creator = request.user, post_img = image)
				post.save()
				return redirect('home-page')
			elif extension.lower() == 'gif':
				post = Post(content = content, post_creator = request.user, post_img = image)
				post.save()
				return redirect('home-page')
			else:
				messages.error(request, 'Invalid image. Please select image type of "jpg", "png" or "gif".')
		else:
			post = Post(content = content, post_creator = request.user)
			post.save()
			return redirect('home-page')


	return render(request, 'bamchat/create_post.html')

@login_required(login_url =  'login-page')
def likePost(request, pk):
	request.session.set_expiry(0)

	post = Post.objects.get(id = pk)
	post.like.add(request.user)
	post.save()
	return redirect ('home-page')

@login_required(login_url =  'login-page')
def unlikePost(request, pk):
	request.session.set_expiry(0)

	post = Post.objects.get(id = pk)
	post.like.remove(request.user)
	post.save()
	return redirect ('home-page')


@login_required(login_url =  'login-page')
def PostComment(request,pk):
	request.session.set_expiry(0)
	post = Post.objects.get(id = pk)
	context = {
				'post_title':str(post.content[:30])+ '...',
				'post':post
			}
	post_and_comment_id = []
	if post.comment:
		
		for i in post.comment.all():
			post_and_comment_id.append(str(i.id)+ '-'+ str(post.id))

		post_and_comment_id.reverse()

		posts_and_comment_id = zip(post_and_comment_id, post.comment.all().order_by('-id') )
		posts_and_comment_id20 = zip(post_and_comment_id[:20], post.comment.all().order_by('-id')[:5])

		context = {
					'post_title':str(post.content[:30])+ '...',
					'post':post,
					'comments':post.comment.all().order_by('-id')[:5],
					'posts_and_comment_id':posts_and_comment_id,
					'posts_and_comment_id20':posts_and_comment_id20,
					'length':len(post.comment.all()),
					
		}

	if request.method == 'POST':
		comment = request.POST.get('comment')
		COMMENT = Comment(text = comment, user = request.user)
		COMMENT.save()
		post.comment.add(COMMENT)
		post.save()
		return redirect('comment', pk = post.id)


	
	return render(request, 'bamchat/comment_page.html',context)

@login_required(login_url =  'login-page')
def blockComment(request,pk):
	post = Post.objects.get(id = pk)
	post.close_comment = True
	post.save()
	return redirect('comment', pk = post.id)

@login_required(login_url =  'login-page')
def unblockComment(request,pk):
	post = Post.objects.get(id = pk)
	post.close_comment = False
	post.save()
	return redirect('comment', pk = post.id)

@login_required(login_url =  'login-page')
def editComment(request,pk):
	# request.session.set_expiry(0)
	comment_id = pk.split('-')[0]
	post_id = pk.split('-')[1]
	print(comment_id)
	print(post_id)
	comment = Comment.objects.get(id =comment_id)
	post = Post.objects.get(id = post_id)
	if comment.user == request.user:
		if request.method == 'POST':
			text = request.POST.get('comment')
			comment.text = text
			comment.save()
			return redirect('comment', pk = post.id)
	else:
		return HttpResponse('You are not authorized to edit this comment')
	context = {
				'comment':comment

	}
	return render(request, 'bamchat/editcomment.html', context)


@login_required(login_url =  'login-page')
def deleteComment(request,pk):
	request.session.set_expiry(0)
	comment_id = pk.split('-')[0]
	post_id = pk.split('-')[1]
	comment = Comment.objects.get(id = comment_id)
	post = Post.objects.get(id = post_id)
	if comment.user == request.user:
		if request.method == 'POST':
			confirm = request.POST.get('confirm')
			if confirm == 'Yes':
				comment.delete()
				return redirect('comment', pk = post.id)
	else:
		return HttpResponse('You are not authorized to delete this comment')
	context = {'delete':True
				}
	return render(request, 'bamchat/editcomment.html', context)

@login_required(login_url =  'login-page')
def editPost(request,pk):
	request.session.set_expiry(0)
	post = Post.objects.get(id = pk)
	if post.post_creator == request.user:
	
		if request.method == 'POST':
			content = request.POST.get('post_content')
			post.content = content
			post.save()
			return redirect('home-page')
	else:
		return HttpResponse('You are not authorized to edit this post')

	context = {'post':post}
	return render(request, 'bamchat/editpost.html', context)

@login_required(login_url =  'login-page')
def deletePost(request,pk):
	request.session.set_expiry(0)
	post = Post.objects.get(id = pk)
	if post.post_creator == request.user:

		if request.method == 'POST':
		
			confirm = request.POST.get('confirm')
			if confirm == 'Yes':
				post.delete()
				return redirect('home-page')

	else:
		return HttpResponse('You are not authorized to delete this post')
	context = { 'post':post,
				'delete':True
				}
	return render(request,'bamchat/editpost.html', context )

@login_required(login_url =  'login-page')
def ViewComments(request,pk):
	request.session.set_expiry(0)
	post = Post.objects.get(id = pk)
	post_comment_id = []
	for i in post.comment.all():
		post_comment_id.append(str(i.id) + '-'+str(post.id))

	posts_comments_id = zip(post.comment.all(), post_comment_id)

	context = {
				'post_title':str(post.content[:30])+ '...',
				# 'post':post,
				'posts_comments_id':posts_comments_id
			}
	
	
	return render(request, 'bamchat/view_comment.html',context)


@login_required(login_url =  'login-page')
def Feedback(request):
	request.session.set_expiry(0)
	if request.method == 'POST':
		from_user = request.user.email
		subject = request.user.username.upper() + ' FEEDBACK FOR BAMCHAT'
		message = request.POST.get('feedback')
		to = [settings.EMAIL_HOST_USER]
		context = {
					'user':request.user.username.upper(),
					"message":message
		}
		html_content = render_to_string('bamchat/feedback_email.html',context)
		text = strip_tags(html_content)
		html_email = EmailMultiAlternatives(subject, html_content,from_user, to )
		html_email.attach_alternative(html_content, 'text/html')
		html_email.send()
		messages.success(request, 'Thank you for your feedback')

	return render(request, 'bamchat/feedback.html')

