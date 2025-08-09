# src/app.py
from flask import Flask, render_template, request, jsonify
from main import MigrationActChatbot

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
chatbot = MigrationActChatbot()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    response = chatbot.process_user_message(user_message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)