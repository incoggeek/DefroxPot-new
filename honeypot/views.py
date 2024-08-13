import time
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import requests
from honeypot import settings
from .Honeypot_Project_final import main
from werkzeug.serving import make_server
import threading
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
server = None
t2 = None


def handle_logs(LOG_FILE_PATH):
    logs = []
    with open(LOG_FILE_PATH, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                # print(line)
                logs.append(json.loads(line))
    return logs


@login_required
def dashboard(request):
    ip_addr = []
    addr = []
    try:
        logs_web = handle_logs(
            './honeypot/Honeypot_Project_final/var/web_honeypot.log')
        for log in logs_web:
            if log['ip_addr'] not in ip_addr:
                ip_addr.append(log['ip_addr'])
        logs_net = handle_logs(
            './honeypot/Honeypot_Project_final/var/net_honeypot.log')
        for log in logs_net:
            try:
                if log['ip_address'] not in ip_addr:
                    ip_addr.append(log['ip_address'])
            except:
                pass
        logs_key = handle_logs(
            './honeypot/Honeypot_Project_final/var/key_logger.log')
        for log in logs_key:
            if log['ip_addr'] not in ip_addr:
                ip_addr.append(log['ip_addr'])

        return render(request, 'dashboard.html', {"active": "dashboard", "ip_addr": ip_addr})
    except:
        return render(request, 'dashboard.html', {"active": "dashboard"})


flask_thread = None
flask_server = None
ftp_thread = None
ssh_thread = None
cloudflared_thread = None


@login_required
def setup(request):
    return render(request, "action.html", {"active": "setup"})


@login_required
def insights(request):
    return render(request, "insights.html", {"active": "insights"})


@login_required
def file_analysis(request):
    try:
        key_logs = handle_logs(
            './honeypot/Honeypot_Project_final/var/file_analysis.log')
        keys = []
        for key_log in key_logs:
            for key in key_log.keys():
                if key not in keys:
                    keys.append(key)
        return render(request, "file.html", {"active": "details", 'key_logs': key_logs, 'keys': keys})
    except:
        return render(request, "file.html", {"active": "details"})


@login_required
def Keylogging(request):
    try:
        key_logs = handle_logs(
            './honeypot/Honeypot_Project_final/var/key_logger.log')
        # print(key_logs)
        keys = []
        for key_log in key_logs:
            for key in key_log.keys():
                if key not in keys:
                    keys.append(key)
        print(keys)
        return render(request, "Keylogging.html", {"active": "Keylogging", 'key_logs': key_logs, 'keys': keys})
    except:
        return render(request, "Keylogging.html", {"active": "Keylogging"})


@login_required
def network(request):
    try:
        key_logs = handle_logs(
            './honeypot/Honeypot_Project_final/var/net_honeypot.log')
        keys = []
        for key_log in key_logs:
            for key in key_log.keys():
                if key not in keys:
                    keys.append(key)
        return render(request, "network-log.html", {"active": "network", 'key_logs': key_logs, 'keys': keys})
    except:
        return render(request, "network-log.html", {"active": "network"})


@login_required
def photo(request):
    try:
        key_logs = handle_logs(
            './honeypot/Honeypot_Project_final/var/photo_metadata.log')
        keys = []
        for key_log in key_logs:
            for key in key_log.keys():
                if key not in keys:
                    keys.append(key)
        return render(request, "photo-meta.html", {"active": "photo", 'key_logs': key_logs, 'keys': keys})
    except:
        return render(request, "photo-meta.html", {"active": "photo"})


@login_required
def website(request):
    try:
        key_logs = handle_logs(
            './honeypot/Honeypot_Project_final/var/web_honeypot.log')
        keys = []
        for key_log in key_logs:
            for key in key_log.keys():
                if key not in keys:
                    keys.append(key)
        return render(request, "web-log.html", {"active": "website", 'key_logs': key_logs, 'keys': keys})
    except:
        return render(request, "web-log.html", {"active": "website"})


@login_required
def about(request):
    return render(request, "about.html", {"active": "about"})


# Functions
@csrf_exempt
def start_flask_server(request):
    global flask_thread, flask_server, cloudflared_thread

    if request.method == 'POST':
        # Start Flask server in a new thread if it's not already running
        if flask_thread is None or not flask_thread.is_alive():
            def run_flask():
                global flask_server
            
                # Start the Flask server
                flask_server = make_server('0.0.0.0', 5000, main.WebsiteTrap.app, threaded=True)
                flask_server.serve_forever()

            flask_thread = threading.Thread(target=run_flask)
            flask_thread.start()
        
        # Start Cloudflared tunnel in a new thread if it's not already running
        if cloudflared_thread is None or not cloudflared_thread.is_alive():
            cloudflared_thread = threading.Thread(
                target=main.CloudFlared.run_cloudflared, args=(1,))
            cloudflared_thread.start()
            time.sleep(5)
            

            #return JsonResponse({'status': 'started', 'ip': ""})
        #else:
            #return JsonResponse({'status': 'already_running'})
        
        return JsonResponse({'status': 'started', 'ip': main.CloudFlared.get_val()})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def stop_flask_server(request):
    global flask_thread, flask_server,cloudflared_thread
    if request.method == 'POST':
        if flask_thread is not None and flask_thread.is_alive():
            flask_server.shutdown()  # Shutdown the server
            flask_thread.join()  # Wait for the thread to finish
            flask_thread = None
            flask_server = None

            main.CloudFlared.run_cloudflared(0)
            cloudflared_thread = None

            return JsonResponse({'status': 'stopped'})
        else:
            return JsonResponse({'status': 'not_running'})
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def start_network_server(request):
    global ftp_thread, ssh_thread
    if request.method == 'POST':
        if ftp_thread is None or not ftp_thread.is_alive():
            ftp_thread = threading.Thread(
                target=main.FtpHoneypot.run_ftp_server)
            ftp_thread.start()

        if ssh_thread is None or not ssh_thread.is_alive():
            ssh_thread = threading.Thread(
                target=main.SSHhoneypot.start_ssh_server)
            ssh_thread.start()
            return JsonResponse({'status': 'started'})
        else:
            return JsonResponse({'status': 'already_running'})
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def stop_network_server(request):
    global ftp_thread, ssh_thread
    if request.method == 'POST':
        if ftp_thread is not None and ftp_thread.is_alive():
            main.FtpHoneypot.stop_ftp_server()
            # Code to stop the FTP server goes here
            ftp_thread.join()
            ftp_thread = None

        if ssh_thread is not None and ssh_thread.is_alive():
            main.SSHhoneypot.stop_ssh_server()
            # Code to stop the SSH server goes here
            ssh_thread.join()
            ssh_thread = None

        return JsonResponse({'status': 'stopped'})
    # return JsonResponse({'status': 'not_running'})

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def network_setup(request):
    global ftp_thread, ssh_thread
    # if request.method == 'POST':
    if (ftp_thread is not None and ftp_thread.is_alive()) or (ssh_thread is not None and ssh_thread.is_alive()):
        return JsonResponse({'status': 'running'})
    return JsonResponse({'status': 'stopped'})

    # return JsonResponse({'error': 'Invalid request method'}, status=400)


def server_setup(request):
    global flask_thread
    if flask_thread is not None and flask_thread.is_alive():
        return JsonResponse({'status': 'running'})
    else:
        return JsonResponse({'status': 'stopped'})


def handlelogin(request):
    if request.method == "POST":
        Username = request.POST["loginusername"]
        Password = request.POST["loginpassword"]
        user = authenticate(username=Username, password=Password)
        if user is not None:
            login(request, user)
            # messages.success(request,"You are successfully logined!!")
            return redirect("dashboard")
        else:
            messages.error(request, "Username or Password is incorrect.")
            return redirect('handlelogin')
    return render(request, 'cpanel.html')


@login_required
def handlelogout(request):
    logout(request)
    messages.info(request, "Logged out Successfully!")
    return redirect('handlelogin')

@login_required
def update(request):

    GITHUB_COMMITS_URL = "https://api.github.com/repos/TeamDefronix/DefroxPot/commits"

    # This should be replaced with a persistent storage (e.g., database)
    last_known_commit_hash = getattr(settings, 'LAST_KNOWN_COMMIT_HASH', None)

    try:
        # Fetch the latest commits from the GitHub API
        response = requests.get(GITHUB_COMMITS_URL)
        response.raise_for_status()
        commits = response.json()

        # Get the latest commit hash
        latest_commit_hash = commits[0]['sha']

        # Check if an update is available
        update_available = latest_commit_hash != last_known_commit_hash

        if update_available:
            # Update the last known commit hash (in production, save this to a database)
            settings.LAST_KNOWN_COMMIT_HASH = latest_commit_hash
            message = "Update is available!"
        else:
            message = "No updates available."

        return JsonResponse({
            'update_available': update_available,
            'message': message
        })
    except requests.RequestException as e:
        return JsonResponse({
            'update_available': False,
            'message': f"Error checking for updates: {str(e)}"
        })
