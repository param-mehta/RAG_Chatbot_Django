import os
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils import timezone
from chatbot.models import Chat
from chatbot.chatbot_utils import *
from django.contrib.auth.decorators import login_required

# Load Google API credentials from environment variable
json_creds = json.loads(os.environ['GOOGLE_API_KEY_STRING'].strip(), strict=False)
project_id = json_creds['project_id']
credentials = service_account.Credentials.from_service_account_info(json_creds)
aiplatform.init(project=project_id, credentials=credentials)

# Constants
DEVICE = 'cpu'
get_llm_response = True

@login_required
def chatbot(request):
    try:
        # Fetch chats for the logged-in user and the current session chat ID
        chats = Chat.objects.filter(user=request.user, chat_id=request.session['chat_id'])
    except:
        # Redirect to login page if session chat ID is not found
        return redirect(login)

    if request.method == 'POST':
        message = request.POST.get('message')
        chat_id = request.session['chat_id']
        session_issue_type = request.session['issue_type']
        answer = 'DUMMY RESPONSE'

        if get_llm_response:
            # Get previous messages in the desired format
            chat_history = get_chat_history(chats)

            # Generate response using QA chain
            response = qa_chain({'question': message, 'chat_history': chat_history})
            answer = response['answer']

        # Save the chat message and response to the database
        chat = Chat(user=request.user, chat_id=chat_id, message=message, response=answer, created_at=timezone.now(), issue_type=session_issue_type)
        chat.save()
        return JsonResponse({'message': message, 'response': answer})

    # Render chatbot.html template with chats
    return render(request, 'chatbot.html', {'chats': chats})

def feedback(request):
    if request.method == 'POST':
        # Get vote from POST data
        vote = request.POST['vote']

        # Update the vote for the last chat entry
        last_chat = Chat.objects.last()
        last_chat.vote = vote
        last_chat.save()

        # Redirect to chatbot page
        return redirect('chatbot')

    # Return method not allowed if accessed via GET
    return HttpResponse("Method Not Allowed", status=405)

def issue_type(request):
    if request.method == 'POST':
        session_issue_type = request.POST.get('issue_type')
        request.session['issue_type'] = session_issue_type
        
        last_chat = Chat.objects.last()
        if last_chat:
            request.session['chat_id'] = last_chat.chat_id + 1
        else:
            request.session['chat_id'] = 1

        if get_llm_response:
            # Initialize language model and embeddings function
            model = ChatVertexAI(model="gemini-pro", max_output_tokens=1000)
            embedding_function = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large", model_kwargs={"device": DEVICE})

            # Load vector embeddings and select relevant prompt
            db = get_db(session_issue_type, embedding_function)
            template = generate_prompt(RAG_FORMAT, session_issue_type)
            prompt = PromptTemplate(template=template, input_variables=["context", "question"])

            global qa_chain
            qa_chain = get_qa_chain(model, db, prompt)

        # Redirect to chatbot page
        return redirect('chatbot')

    # Render issue_type.html template
    return render(request, 'issue_type.html')

def login(request):
    if request.method == 'POST':
        # Authenticate user with provided username and password
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)

        # If user is authenticated, redirect to issue_type page
        if user is not None:
            auth.login(request, user)
            return redirect('issue_type')
        else:
            # If authentication fails, render login page with error message
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})

    # Render login.html template for GET requests
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        # Process user registration
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # Validate passwords match
        if password1 == password2:
            try:
                # Create user and login if registration succeeds
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('issue_type')
            except:
                # Render registration page with error message if registration fails
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            # Render registration page with error message if passwords don't match
            error_message = 'Passwords do not match'
            return render(request, 'register.html', {'error_message': error_message})

    # Render registration page for GET requests
    return render(request, 'register.html')

def logout(request):
    # Logout user and redirect to login page
    auth.logout(request)
    return redirect('login')
