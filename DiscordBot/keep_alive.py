## Import the necessary modules for this file
from flask import Flask
from threading import Thread

web = Flask('') ## Create an instance of a 'Flask' object

@web.route('/')
def home():
   return "I am alive!"

def run():
  web.run(host='0.0.0.0',port=8080)

## Keep the thread alive
def keep_alive():
   run_thread = Thread(target=run)
   run_thread.start()