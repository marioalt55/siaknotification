from flask import Flask
from src.siaknotification import siak_notify

app = Flask(__name__)

@app.route('/siak-notify', methods=['GET'])
def siak_notify_controller():
    siak_notify()
    return "Called siak notify function!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)