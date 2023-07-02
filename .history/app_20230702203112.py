from flask import Flask, render_template, Response
import redis
import datetime

app = Flask(__name__)
r = redis.Redis(host='192.168.100.18', port=6379, db=0)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/time')
def time_stream():
    def generate_time():
        pubsub = r.pubsub()
        pubsub.subscribe('time')

        for message in pubsub.listen():
            if message['type'] == 'message':
                current_time = datetime.datetime.now().strftime("%H")
                yield f"data: {current_time}\n\n"

    return Response(generate_time(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)