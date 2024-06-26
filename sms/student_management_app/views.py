from django.shortcuts import render,HttpResponse, redirect,HttpResponseRedirect
from django.contrib.auth import logout, authenticate, login
from .models import CustomUser, Staffs, Students, AdminHOD
from django.contrib import messages

def home(request):
	return render(request, 'home.html')


def contact(request):
	return render(request, 'contact.html')


def loginUser(request):
	return render(request, 'login_page.html')

def doLogin(request):
	
	print("here")
	username = request.GET.get('username')
	password = request.GET.get('password')
	# user_type = request.GET.get('user_type')
	print(username)
	print(password)
	print(request.user)
	if not (username and password):
		messages.error(request, "Please provide all the details!!")
		return render(request, 'login_page.html')

	#user = CustomUser.objects.filter(username=username, password=password).last()
	user = authenticate(username=username,password=password)
	if not user:
		messages.error(request, 'Invalid Login Credentials!!')
		return render(request, 'login_page.html')

	login(request, user)
	print(request.user)

	if user.user_type == CustomUser.STUDENT:
		return redirect('student_home/')
	elif user.user_type == CustomUser.STAFF:
		return redirect('staff_home/')
	elif user.user_type == CustomUser.HOD:
		return redirect('admin_home/')

	return render(request, 'home.html')

	
def registration(request):
	return render(request, 'registration.html')
	

def doRegistration(request):
	first_name = request.GET.get('first_name')
	last_name = request.GET.get('last_name')
	email_id = request.GET.get('email')
	password = request.GET.get('password')
	confirm_password = request.GET.get('confirmPassword')

	print(email_id)
	print(password)
	print(confirm_password)
	print(first_name)
	print(last_name)
	if not (email_id and password and confirm_password):
		messages.error(request, 'Please provide all the details!!')
		return render(request, 'registration.html')
	
	if password != confirm_password:
		messages.error(request, 'Both passwords should match!!')
		return render(request, 'registration.html')

	is_user_exists = CustomUser.objects.filter(email=email_id).exists()

	if is_user_exists:
		messages.error(request, 'User with this email id already exists. Please proceed to login!!')
		return render(request, 'registration.html')

	user_type = get_user_type_from_email(email_id)

	if user_type is None:
		messages.error(request, "Please use valid format for the email id: '<username>.<staff|student|hod>@<college_domain>'")
		return render(request, 'registration.html')

	username = email_id.split('@')[0].split('.')[0]

	if CustomUser.objects.filter(username=username).exists():
		messages.error(request, 'User with this username already exists. Please use different username')
		return render(request, 'registration.html')

	user = CustomUser()
	user.username = username
	user.email = email_id
	user.set_password(password)
	user.user_type = user_type
	user.first_name = first_name
	user.last_name = last_name
	user.save()
	
	if user_type == CustomUser.STAFF:
		Staffs.objects.create(admin=user)
	elif user_type == CustomUser.STUDENT:
		Students.objects.create(admin=user)
	elif user_type == CustomUser.HOD:
		AdminHOD.objects.create(admin=user)
	return render(request, 'login_page.html')

	
def logout_user(request):
	logout(request)
	return HttpResponseRedirect('/')


def get_user_type_from_email(email_id):
	"""
	Returns CustomUser.user_type corresponding to the given email address
	email_id should be in following format:
	'<username>.<staff|student|hod>@<college_domain>'
	eg.: 'abhishek.staff@jecrc.com'
	"""

	try:
		email_id = email_id.split('@')[0]
		email_user_type = email_id.split('.')[1]
		return CustomUser.EMAIL_TO_USER_TYPE_MAP[email_user_type]
	except:
		return None






# chatbot/views.py
from django.shortcuts import render
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from .models import Question, Response

def get_response_from_database(user_input):
    questions = Question.objects.all()
    matched_question, score = process.extractOne(user_input, [q.text for q in questions])

    # You can adjust the threshold as needed
    if score >= 50:
        # If the similarity score is above a certain threshold, retrieve the response
        try:
            question = Question.objects.get(text__iexact=matched_question)
            response = Response.objects.get(question=question)
            return response.text
        except Question.DoesNotExist:
            return "I'm sorry, I don't know the answer to that question."
        except Response.DoesNotExist:
            return "I don't have a response for that question yet."
    else:
        return "I'm sorry, I don't understand. Can you please rephrase your question?"

def chatbot(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        response = get_response_from_database(user_input)
        return render(request, 'chatbot/chatbot.html', {'user_input': user_input, 'response': response})

    return render(request, 'chatbot/chatbot.html')