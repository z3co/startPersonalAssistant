import platform
import speech_recognition as sr #pip install SpeechRecognition
import pyttsx3
import threading
import subprocess
import psutil
import time
import re
import os
import webbrowser
import time
import datetime
import logging
import ctypes
import win32gui
import win32con
import requests
from dotenv import load_dotenv
from github import GitHub
from github import Auth
import tkinter as tk
from tkinter import scrolledtext
from sys import argv
import json

#Idea for later use make a ui with tkinter

load_dotenv()

os.system('title Start Personal Assistant')

listening_for_keyword = True

logging.basicConfig(
    filename=r"C:\Users\Jeppe\Codes\In progress\StartPersonalAssistant\pokedex.txt",
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.ERROR
)

def get_current_time():
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time

def get_current_date():
    now = datetime.datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    return current_date

def text_to_speech(talk):


    engine = pyttsx3.init()

    engine.setProperty('rate', 170)

    engine.say(talk)
    engine.runAndWait()


def listen_for_keyword(keyword):
    global listening_for_keyword
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    
    while listening_for_keyword:
        if game_running:
            time.sleep(1)
            continue
        
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            
            try:
                audio = recognizer.listen(source)
                speech = recognizer.recognize_google(audio).lower()
                print()
                if keyword in speech:
                    bring_window_to_focus()
                    print(f"keyword detected now listening...")
                    text_to_speech("What can i do for you")
                    transcribbed_text = record_and_transcribe()
                    if transcribbed_text:
                        process_command(transcribbed_text)
            except sr.UnknownValueError:
                print("Unkown value error") #Again?
            except sr.RequestError as e:
                print(f"error fetching results")
                error_handling(e, "Error fetching results for keyword") 
            except Exception as e:
                error_handling(e, "Unknown error in listening for keyword")


def record_and_transcribe():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        print("Recording...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio)
            return text.lower()
        except sr.UnknownValueError:
            print("Could not understand audio") #Every F***** time
            return None
        except sr.RequestError as e:
            respond(f"Error fetching results")
            error_handling(e, "Error fetching results while recording and transcribing") 
            return None
        except Exception as e:
            print(f'You caught an error')
            error_handling(e, "Unknown error while recording and transcribing")  #Maybe this is not needed?
            return None
        
def process_commands(commands): #F****** useless
    for command in commands:
        command = command.strip()
        if command:
            process_command(command)

#Make this better
def ask_question(question, type):
    respond(question)

    global listening_for_keyword
    listening_for_keyword = False
    
    results = {'voice': None, 'keyboard': None}
    input_received = threading.Event()

    def record_and_transcribe_wrapper(results):
        while not input_received.is_set():
            result = record_and_transcribe()
            if result:
                results['voice'] = result
                input_received.set()
                break

    def keyboard_input_commands_for_question_wrapper(results):
        while not input_received.is_set():
            result = keyboard_input_commands_for_question()
            if result:
                results['keyboard'] = result
                input_received.set()
                break

    voice_answer_thread = threading.Thread(target=record_and_transcribe_wrapper, args=(results,))
    keyboard_answer_thread = threading.Thread(target=keyboard_input_commands_for_question_wrapper, args=(results,))

    voice_answer_thread.start()
    keyboard_answer_thread.start()

    input_received.wait()

    voice_answer_thread.join(timeout=0)
    keyboard_answer_thread.join(timeout=0)

    try:
        voice_result = results['voice']
        keyboard_result = results['keyboard']

        if not voice_result and not keyboard_result:
            print("No valid input detected")
            listening_for_keyword = True
            return True
        else:
            transcribed_text = voice_result if voice_result else ""
            transcribed_text_keyboard = keyboard_result if keyboard_result else ""
            if transcribed_text:
                process_question(transcribed_text, type)
            elif transcribed_text_keyboard:
                process_question(transcribed_text_keyboard, type)
            else:
                print("No transcribed text")
                listening_for_keyword = True
                return
    except Exception as e:
        listening_for_keyword = True
        error_handling(e, "Getting answer for question")
        return

def keyboard_input_commands():
    while True:
        text = input("What do you wanna do?:").lower()
        process_command(text)

def keyboard_input_commands_for_question():
    try:
        text = input("Answer:").lower()
        if text:
            return text
        else:
            return None
    except Exception as e:
        error_handling(e, "Getting keyboard input for question")
        return None
    

    
def process_command(text):
    print(f"Processing command text: {text}") #If im lucky

    global game_running, listening_for_keyword
    if game_running:
        print("A game is running. No commands can be processed") #Hopefully
        return

    try:
        if re.search(r'\b(hello| hi|hey)\b', text) or re.search(r'\bhi\b', text):
            respond("Hello what can i do for you")
            record_and_transcribe_and_process()
        elif re.search(r'\bexit\b', text):
            respond("goodbye, just say my name if you need me")
            listening_for_keyword = True
            return
        elif re.search(r'\bstop\b', text):
            respond("Stopped listening, to start simply write start")

            listening_for_keyword = False
            return True
        elif re.search(r'\bplay\b', text) or re.search(r'\bgame\b', text):
            ask_question("sure, what do you want to play", "game")
        elif re.search(r'\bstart\b', text):
            listening_for_keyword = True
            respond("Starting to listen")
            listening_for_keyword = True
            voice_thread = threading.Thread(target=listen_for_keyword, args=(keyword,))
            keyboard_thread = threading.Thread(target=keyboard_input_commands)

            voice_thread.start()
            keyboard_thread.start()

            voice_thread.join()
            keyboard_thread.join()

        elif re.search(r'\b(shut down|shutdown|power off)\b', text):
            respond("Shutting down")
            shutdown_computer()
        elif re.search(r'\bsearch\b', text):
            query = text.replace('search', '').strip()
            respond(f"Searching for {query}")
            search_web(query) 
        elif re.search(r'\bthrow.error\b', text):
            error = "Did it work"
            error_handling(error, "test")
        elif re.search(r'\btake notes\b', text):
            ask_question("Sure, what would you like to note", "note")
        elif re.search(r'\bread\b', text) and re.search(r'\bnote|notes\b', text):
            read_notes()
        elif re.search(r'\bfind\b', text) and re.search(r'\b(note|notes)\b', text):
            respond("Finding note")
            ask_question("What is the note you are looking for", "search_notes")
        elif re.search(r"\b(plus|add|multiply|divide|minus|subtract)\b", text):
            result = calculate(text)
            if result is not None:
                respond(f"Sure, it makes: {result}")
            else:
                respond(f"Something went wrong while calculating, as there are no result")
        elif re.search(r"\bcreate\b", text) and re.search(r"project", text):
            ask_question("What should i call the new project", "create_new_project")
        elif re.search(r"\btest\b", text):
            respond("Test")
        elif re.search(r"\b(upload|publish)\b", text) and re.search(r"\b(video|meme)\b", text):
            respond("Publishing video")
            subprocess.run(r"C:\Users\Jeppe\Desktop\Upload_video.bat")
        elif re.search(r"\bopen\b", text) and re.search(r"\bproject\b", text):
            project1 = text.replace('open', '').strip()
            project2 = project1.replace('project', '').strip()
            if project2 != '':
                if project2 == 'start':
                    project = "C:\\Users\\Jeppe\\Codes\\In progress\\StartPersonalAssistant"
                elif project2 == 'whatmeme':
                    project = "C:\\Users\\Jeppe\\Codes\\In progress\\autoytvideo"
                elif project2 == 'dataserver':
                    project = "C:\\Users\\Jeppe\\Codes\\In progress\\startdataserver"
                elif project2 == 'cloudwebserver':
                    project = "C:\\Users\\Jeppe\\Codes\\Done\\cloudWebServer"
                else:
                    project = "C:\\Users\\Jeppe\\Codes\\In progress\\StartPersonalAssistant"
                respond(f"Opening {project2}")
                open_in_vscode(project)
            else:
                ask_question("what project are we working on today", "project")
        else:
            respond("Sorry, i dont understand that") #Yeah it isnt very smart
            return
    except Exception as e:
        error_handling(e, "process_command - general")

def process_question(text, type):
    print(f"Processing question text: {text}") #If im lucky
    global game_running, listening_for_keyword
    listening_for_keyword = True
    try:    

        if type == "game":
            if re.search(r'\bcounter strike\b', text):
                    respond("Opening CS2")
                    run_steam_game("730")
                    time.sleep(5)
                    monitor_program_closure("cs2.exe")
                    return
            elif re.search(r'\bcookie clicker\b', text): #Just in case
                    respond("Opening Cookie Clicker")
                    run_game(r"C:\Program Files (x86)\Steam\steamapps\common\Cookie Clicker\Cookie Clicker.exe")
                    monitor_program_closure("Cookie Clicker.exe")
                    return
            elif re.search(r'\brainbow six\b', text):
                    respond("Opening Rainbow Six Siege")
                    run_steam_game("359550")
                    time.sleep(60)
                    monitor_program_closure("RainbowSix.exe")
                    return
            elif re.search(r'\bred dead redemption\b', text):
                    respond("Opening Red Dead Redemption 2")
                    run_steam_game("1174180")
                    time.sleep(60)
                    monitor_program_closure("RDR2.exe")
                    return
            elif re.search(r"\bsubnautica\b", text):
                    respond("Opening Subnautica")
                    run_steam_game("264710")
                    time.sleep(10)
                    monitor_program_closure("Subnautica.exe")
                    return
            elif re.search(r"\bphasmophobia\b", text): 
                    respond("Opening Phasmophobia")
                    run_steam_game("739630")
                    time.sleep(30)
                    monitor_program_closure("Phasmophobia.exe")
                    return
            elif re.search(r"\bpoker\b", text):
                    respond("Good, luck")
                    pokerurl = r"https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwik4b-y_viGAxXonf0HHQ7DC_UQFnoECBMQAQ&url=https%3A%2F%2Fwww.pokernow.club%2F&usg=AOvVaw2JBQj6EQP5pXstc-NO6AEP&opi=89978449"
                    webbrowser.open(pokerurl)
            elif re.search(r"\bhogwarts legacy", text):
                respond("Opening Hogwarts Legacy")
                subprocess.Popen([r"C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win64\EpicGamesLauncher.exe"])
                time.sleep(30)
                run_game(r"C:\Program Files\Epic Games\HogwartsLegacy\HogwartsLegacy.exe")
                time.sleep(10)
                monitor_program_closure("HogwartsLegacy.exe")
                return
            elif re.search(r"\bjedi survivor", text):
                respond("Opening Star Wars Jedi Survivor")
                run_steam_game("1774580")
                time.sleep(10)
                monitor_program_closure("JediSurvivor.exe")
                return
            else:
                respond("I'm sorry, I dont recognize that game")
                logging.error("Error in recognizing game: Game not found")
                keyboard_input_commands()
                listening_for_keyword = True
                
                return
        
        elif type == "note":
            take_note(text)
            respond("Note saved successfully")
            return
        
        elif type == "search_notes":
            note = search_notes(text)
            if note:
                respond(f"Found note: {note.strip()}")
            else:
                respond("I couldn't find that note")
                logging.error(f"Error in searching notes: Note not found")
                return

        elif type == "create_new_project":
            create_new_project(text)

        elif type == "project":
            if text == 'start':
                project = "C:\\Users\\Jeppe\\Codes\\In progress\\StartPersonalAssistant"
            elif text == 'whatmeme':
                  project = "C:\\Users\\Jeppe\\Codes\\In progress\\autoytvideo"
            elif text == 'dataserver':
                 project = "C:\\Users\\Jeppe\\Codes\\In progress\\startdataserver"
            elif text == 'cloudwebserver':
                project = "C:\\Users\\Jeppe\\Codes\\Done\\cloudWebServer"
            else:
                project = "C:\\Users\\Jeppe\\Codes\\In progress\\StartPersonalAssistant"
            respond(f"Opening {text}")
            open_in_vscode(project)

        else:
                print("Error")
                logging.error("Error in recognizing type: Type not found")
                return
    except Exception as e:
        error_handling(e, "process command - questions")

def respond(response_text):
    try:
        
        
        bring_window_to_focus()
        print(response_text)
        text_to_speech(response_text)
    except Exception as e:
        error_handling(e, "Respond - general")
    
    

def run_game(game_executable):
    try:
        if os.path.exists(game_executable):
            subprocess.run([game_executable])
            global game_running
            game_running = True
        else:
            error_handling("Cannot find game executable", "Running game - general") 
        return
    except Exception as e:
        error_handling(e, "Running game - general")
def is_program_running(program_name):
    for process in psutil.process_iter(['name']):
        if process.info['name'] == program_name:
            return True
    return False
    

def monitor_program_closure(program_name):
    while True:
        if not is_program_running(program_name):
            print(f"{program_name} has closed")
            global game_running, listening_for_keyword
            listening_for_keyword = True
            game_running = False
            respond("Game closed, call my name if you need me")


            listen_thread = threading.Thread(target=listen_for_keyword, args=(keyword,))
            keyboard_thread = threading.Thread(target=keyboard_input_commands)

            listen_thread.start()
            keyboard_thread.start()

            listen_thread.join()
            keyboard_thread.join()


            break
        time.sleep(10)

def run_steam_game(app_id):
    if platform.system() == "Windows":
        steam_path = r"C:\Program Files (x86)\Steam\steam.exe"
    elif platform.system() == "Darwin":
        steam_path = "/Applications/Steam.app/Contents/MacOS/steam_osx"
    else:
        steam_path = "/usr/bin/steam"

    try:
        subprocess.run([steam_path, "-applaunch", app_id])
        global game_running
        global listening_for_keyword
        listening_for_keyword = False
        game_running = True
    except Exception as e:
        error_handling(e, "Running game - Steam")

def shutdown_computer():
    if platform.system() == "Windows":
        os.system("shutdown /s /t 1")
    elif platform.system() == "Darwin" or platform.system() == "Linux":
        os.system("shutdown -h now")
    else:
        respond("Sorry i dont know how to shutdown your operating system")
    

def record_and_transcribe_and_process():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        print("Recording...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio)
            process_command(text)
            return text.lower()
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            respond(f"Error fetching results; {e}")
            return None
        except Exception as e:
            error_handling(e) 
        
def search_web(query): 
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)


def error_handling(error, place): #In case my code is as bad as i think it is
        print("Error")
        logging.error(f"Error in {place}: {error} \n")

def take_note(note):
    with open(r"C:\Users\Jeppe\Codes\In progress\StartPersonalAssistant\notes.txt", "a") as file:
        timestamp = get_current_time()
        date = get_current_date()
        file.write(f"{note}\n")
        print("Note added to file: notes.txt")

def read_notes():
    if os.path.exists(r"C:\Users\Jeppe\Codes\In progress\StartPersonalAssistant\notes.txt"):
        with open(r"C:\Users\Jeppe\Codes\In progress\StartPersonalAssistant\notes.txt", 'r' ) as file:
            notes = file.readlines()
    if notes:
        for note in notes:
            respond(note)
    else:
        respond("No notes found in notes.txt")

def search_notes(query):
    if os.path.exists(r"C:\Users\Jeppe\Codes\In progress\StartPersonalAssistant\notes.txt"):
        with open(r"C:\Users\Jeppe\Codes\In progress\StartPersonalAssistant\notes.txt", 'r') as file:
            notes = file.readlines()
        matching_notes = [note.strip() for note in notes if query in note.lower()]
        if matching_notes:
            for note in matching_notes:
                return note
        else:
            error_handling("No matching notes found", "Search for note")
    else:
        error_handling("No notes", "Search for notes")

def bring_window_to_focus():
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd != 0:

        try:
            win32gui.SetForegroundWindow(hwnd)
        except Exception as e:
            error_handling(e, "Bringing window to focus, problem most likely fixed itself")

            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                  win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            time.sleep(0.1)
            win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                  win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            
def calculate(text):
    try:

        def extract_numbers(text):
            found_numbers = re.findall(r'\d+', text)

            return [int(num) for num  in found_numbers]
        
        #add 2 and 2
        #query = text.replace('search', '').strip()
        if re.search(r"\b(plus|add)\b", text):
            numbers = extract_numbers(text)
            if len(numbers) >= 2:
                result = sum(numbers)
                return result
            else:
                logging.error("Error in adding: Less than 2 numbers")
                return None
        elif re.search(r"\b(minus|subtract)\b", text):
            numbers = extract_numbers(text)
            if len(numbers) >= 2:
                result =numbers[0]
                for number in numbers[1:]:
                    result -= number
                    return result
            else:
                logging.error("Error in subtracting: Less than 2 numbers")
                return None
        elif re.search(r"\b(multiply)\b", text):
            numbers = extract_numbers(text)
            if len(numbers) >= 2:
                product = 1
                for number in numbers:
                    product *= number
                return product
            else:
                logging.error("Error in multiplying: Less than 2 numbers")
                return None
        elif re.search(r"\b(divide)\b", text):
            numbers = extract_numbers(text)
            if len(numbers) >= 2:
                result = numbers[0]
                try:
                    for number in numbers[1:]:
                        result /= number
                    return result
                except ZeroDivisionError:
                    logging.error("Error in Dividing: Cannot divide by 0")
                    return None
            else:
                logging.error("Error in Dividing: Less than 2 numbers")
                return None
        else:
            error_handling("Unkown calculating method", "Calculating")
            return None
    except Exception as e:
        error_handling(e, "Calculating")
        return None

def create_folder(folder_path):
    try:
        os.makedirs(folder_path, exist_ok=True)
        print(f"Folder {folder_path} created successfully.")
    except Exception as e:
        error_handling(e, "Creating folder")

def create_file(file_path):
    try:
        with open(file_path, 'w') as file:
            file.write("")
        print(f"File {file_path} created successfully.")
    except Exception as e:
        error_handling(e, "Creating file")

def create_new_project(project_name):

    def project_laungage_handler():
        text = input('What is the language for this project:')
        if "javascript" in text.lower():
            return "js"
        elif "python" in text.lower():
            return "py"
        elif "html" in text.lower():
            return "html"
        elif "java" in text.lower():
            return "java"
        else:
            return "py"

    try:
        folder_path = r"C:\Users\Jeppe\Codes\In progress\{}".format(project_name)
        project_launguage = project_laungage_handler()
        filepath = os.path.join(folder_path, f"index.{project_launguage}")
        is_private = input("Is this project private (yes or no):")
        if is_private.lower() == "yes":
            is_private = True
        elif is_private.lower() == "no":
            is_private = False

        
        print(folder_path)
        create_folder(folder_path)
        create_file(filepath)

        create_github_repository(project_name, is_private)

        open_in_vscode(folder_path)
        
    except Exception as e:
        error_handling(e, "Creating new project")

def create_github_repository(project_name, is_private):
    try:
        GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
        

        print(GITHUB_TOKEN)
        g = GitHub(GITHUB_TOKEN)
        user = g.get_user()
        repo = user.create_repo(project_name, private=is_private)

        




        print(f"Created repository: {project_name}")
    except Exception as e:
        error_handling(e, "Creating github repo")

def open_in_vscode(file_path):
    try:
        subprocess.run(["code", file_path], shell=True)
    except Exception as e:
        error_handling(e, "Opening in VS Code")

def main():
    try:
        respond("Hello my name is start, i am your personal assistant, just call my name if you need me")

    

        
        voice_thread = threading.Thread(target=listen_for_keyword, args=(keyword,))
        keyboard_thread = threading.Thread(target=keyboard_input_commands)

        voice_thread.start()
        keyboard_thread.start()

        voice_thread.join()
        keyboard_thread.join()

        


    except Exception as e:
        error_handling(e, "startup")



                
            

if __name__ == "__main__": #and why wouldnt it
 

    bring_window_to_focus()

    keyword = "start"
    global forceUI
    forceUI = False


    game_running = False

    if argv.__contains__("--command"):
        command = argv[argv.index("--command") + 1]
        process_command(command)
    elif argv.__contains__("-C"):
        command = argv[argv.index("-C") + 1]
        process_command(command)
    else:


        if argv.__contains__("--forceUI"):
            forceUI = True
            password = input("Enter password: ")
            text_to_speech("Sending password: " + password)
            data = { 'code':password }
            data_json = json.dumps(data)
            subprocess.Popen("node server.js")
            response = requests.post("http://localhost:5289/set-password", json={'code':password}) 
        else:
            main()
        