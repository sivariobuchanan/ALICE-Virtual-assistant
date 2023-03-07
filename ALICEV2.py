import os
import random
import subprocess
import sys
import time
import webbrowser
import wikipedia
import vlc
from gtts import gTTS
from googlesearch import search
import speech_recognition as sr
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set up some global variables
player = None
instance = None
r = sr.Recognizer()
youtube_api_key = "Api key"  # Replace with your own API key


def get_time():
    return time.strftime("%I:%M %p")


def greet():
    speak("what do you need?")


def speak(text):
    tts = gTTS(text=text, lang='en-gb')
    tts.save("output.mp3")
    subprocess.run(["ffplay", "-nodisp", "-autoexit", "output.mp3"], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    os.remove("output.mp3")


def handle_input(user_input, music_folder):
    commands = {
        "who made you": lambda: speak("I was programmed by Sivario Buchanan."),
        "what is your name": lambda: speak("I am Alice V1.0.0."),
        "who do you love": lambda: speak(
            "I am not programmed to feel what you call love. Although I do think Python is cute tho."),
        "are you happy": lambda: speak("I do not understand the term 'happy'. I am stable and working."),
        "who are you": lambda: speak(
            "I am Alice V1.0.0,\n\nI am a virtual assistant to help with daily tasks.\n\nI can do "
            "whatever my creator programs me to do."),
        "whats the time": lambda: speak(f"The current time is now {get_time()}"),
        "play music": lambda: play_music(music_folder),
        "stop music": lambda: stop_music(),
        "yt": lambda: search_youtube(user_input),
        "spotify": lambda: webbrowser.open("https://open.spotify.com/"),
        "open calculator": lambda: subprocess.run(["calc"]),
        "web": lambda: webbrowser.open("https://www.google.com/"),
        "open terminal": lambda: subprocess.run(["gnome-terminal"]),
        "search": lambda: search_google(user_input),
        "exit": lambda: (speak("Goodbye!"), exit())
    }
    command = next((key for key in commands if key in user_input.lower()), None)
    if command is not None:
        commands[command]()
        if command == "exit":
            exit()
    else:
        wikipedia_search(user_input)


def wikipedia_search(user_input):
    try:
        page = wikipedia.search(user_input, results=1)[0]
        summary = wikipedia.summary(page)
        speak(summary)
    except wikipedia.exceptions.DisambiguationError as e:
        speak(f"Sorry, I'm not sure which page you're looking for. Please try again with a more specific search term.")
    except wikipedia.exceptions.PageError:
        speak("Sorry, I could not find any results.")


def play_music(music_folder):
    speak("let me play you a bop...")
    music_files = os.listdir(music_folder)
    media_list = instance.media_list_new([os.path.join(music_folder, file) for file in music_files])
    media_list_player = instance.media_list_player_new()
    media_list_player.set_media_list(media_list)
    media_list_player.play()

    # Playback control commands
    while True:
        command = input("Enter 'n' to play the next song, 'p' to pause/resume playback, or 'q' to exit: ")
        os.system("clear")
        if command.lower() == "n.":
            media_list_player.next()
        elif command.lower() == "p.":
            if media_list_player.get_state() == vlc.State.Playing:
                media_list_player.pause()
                speak("paused.")
                print("Playback paused.")
            elif media_list_player.get_state() == vlc.State.Paused:
                media_list_player.play()
                print("Playback resumed.")
        elif command.lower() == "q.":
            media_list_player.stop()
            break
        else:
            print("Invalid command. Please try again.")


def stop_music():
    speak("stopping the bop")
    player.stop()


def search_google(query):
    speak("i will" + query)
    for result in search(query, num_results=5):
        webbrowser.open(result)


def search_youtube(query):
    speak("Okay playing" + query)
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
    search_response = youtube.search().list(
        q=query,
        type='video',
        part='id,snippet',
        maxResults=1
    ).execute()

    video_id = search_response['items'][0]['id']['videoId']
    video_url = f'https://www.youtube.com/watch?v={video_id}&autoplay=1'
    webbrowser.open(video_url)

    video_id = search_response['items'][0]['id']['videoId']
    video_url = f'https://www.youtube.com/watch?v={video_id}'
    webbrowser.open(video_url)


def speech_to_text():
    with sr.Microphone() as source:
        print("Speak anything...")
        audio = r.listen(source, timeout=5, phrase_time_limit=5)
        try:
            text = r.recognize_google(audio)
            print("You said: " + text)
            return text
        except sr.UnknownValueError:
            print("Sorry, I could not understand what you said.")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))


def main():
    global player, instance
    instance = vlc.Instance("--no-xlib")
    player = instance.media_player_new()

    music_folder = "Music"

    greet()

    while True:
        try:
            user_input = input("")
            handle_input(user_input, music_folder)
        except KeyboardInterrupt:
            speak("bye")
            exit()


if __name__ == "__main__":
    main()
