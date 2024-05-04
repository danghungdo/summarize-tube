from django.shortcuts import render, redirect
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pytube import YouTube
from django.conf import settings
from decouple import config
from .models import Summary

import assemblyai as aai
import openai
import json
import os

# Create your views here.
def index(request):
    return render(request, 'index.html')

from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render

def user_login(request):
    """
    Logs in a user with the provided credentials.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate the user with the provided credentials
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # If the user is authenticated, log them in and redirect to the home page
            login(request, user)
            return redirect('/')
        else:
            # If the user is not authenticated, display an error message on the login page
            error_message = 'Invalid Credentials'
            return render(request, 'login.html', {'error_message': error_message})
    return render(request, 'login.html')

def user_logout(request):
    """
    Logs out the current user and redirects to the home page.

    Args:
        request: The HTTP request object.

    Returns:
        A redirect response to the home page.
    """
    logout(request)
    return redirect('/')

def user_signup(request):
    """
    Handles the user signup process.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    """
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        repeat_password = request.POST.get('repeatPassword')
        
        if not username or not email or not password or not repeat_password:
            error_message = 'Please fill in all fields'
            return render(request, 'signup.html', {'error_message': error_message})
        
        # check if username already exists
        if User.objects.filter(username=username).exists():
            error_message = 'Username already exists'
            return render(request, 'signup.html', {'error_message': error_message})
        
        # check if email already exists
        if User.objects.filter(email=email).exists():
            error_message = 'Email already exists'
            return render(request, 'signup.html', {'error_message': error_message})
        
        # check if passwords match
        if password != repeat_password:
            error_message = 'Passwords do not match'
            return render(request, 'signup.html', {'error_message': error_message})
        else:
            try:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                login(request, user)
                return redirect('/')
            except:
                error_message = 'Error creating user, please try again'
                return render(request, 'signup.html', {'error_message': error_message})
    
    return render(request, 'signup.html')

def user_logout(request):
    """
    Logs out the current user and redirects to the home page.

    Args:
        request: The HTTP request object.

    Returns:
        A redirect response to the home page.
    """
    logout(request)
    return redirect('/')

@csrf_exempt
def summarize(request):
    """
    Summarizes a YouTube video based on its transcript.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing the video summary and title, or an error message.

    Raises:
        KeyError: If the request body does not contain the 'video_url' key.
        JSONDecodeError: If the request body is not a valid JSON.

    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            video_url = data['video_url']
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid request body'}, status=400)

        # get youtube video title
        title = YouTube(video_url).title
        # get the transcript of the video
        transcript = get_transcript(video_url)
        if not transcript:
            return JsonResponse({'error': 'Could not get transcript'}, status=500)
        
        # use OpenAI to summarize the transcript
        summary = summarize_transcript(transcript)
        if not summary:
            return JsonResponse({'error': 'Could not summarize text'}, status=500)
        # save the video summary to the database
        if request.user.is_authenticated:
            new_summary = Summary.objects.create(
                user=request.user,
                video_url=video_url,
                video_title = title,
                summary=summary,
            )
            new_summary.save()      
        return JsonResponse({'summary': summary, 'title': title}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
 
def download_audio(video_url):
    """
    Downloads the audio from a YouTube video given its URL.

    Args:
        video_url (str): The URL of the YouTube video.

    Returns:
        str: The path of the downloaded audio file.
    """
    yt = YouTube(video_url)
    audio = yt.streams.filter(only_audio=True).first()
    audio_file = audio.download(output_path=settings.MEDIA_ROOT)
    base, ext = os.path.splitext(audio_file)
    new_file = base + '.mp3'
    os.rename(audio_file, new_file)
    return new_file


def get_transcript(video_url):
    """
    Retrieves the transcript of a video given its URL.

    Args:
        video_url (str): The URL of the video.

    Returns:
        str: The transcript of the video.
    """
    audio_file = download_audio(video_url)
    aai.settings.api_key = config('AAI_API_KEY')
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)
    os.remove(audio_file)
    return transcript.text
    
def summarize_transcript(transcript):
    """
    Summarizes the given transcript from a YouTube video using OpenAI's GPT-3.5 Turbo model.

    Args:
        transcript (str): The transcript of the YouTube video.

    Returns:
        str: The comprehensive summary of the transcript, covering all key points and main ideas in a concise format.
    """
    openai.api_key = config('OPENAI_API_KEY')
    prompt = f"Can you provide a comprehensive summary of the following transcript from a YouTube video? The summary should cover all the key points and main ideas presented in the original video, while also condensing the information into a concise and easy-to-understand format. Please ensure that the summary includes relevant details and examples that support the main ideas, while avoiding any unnecessary information or repetition. The length of the summary should be appropriate for the length and complexity of the transcript, providing a clear and accurate overview without omitting any important information:\n\n{transcript}\n\nSummary:"
    response = openai.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=1000
    )
    return response.choices[0].text
    
def history(request):
    """
    Displays the summary history of the current user.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    """
    if request.user.is_authenticated:
        summaries = Summary.objects.filter(user=request.user)
        return render(request, 'history.html', {'summaries': summaries})
    else:
        return redirect('/login')
    
def show_detail(request, summary_id):
    """
    Displays the details of a specific summary.

    Args:
        request (HttpRequest): The HTTP request object.
        summary_id (int): The ID of the summary to display.
    """
    summary = Summary.objects.get(pk=summary_id)
    if request.user == summary.user:
        return render(request, 'detail.html', {'summary_detail': summary})
    else:
        return redirect('/')