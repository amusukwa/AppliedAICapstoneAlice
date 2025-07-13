from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
#CORS(app)
CORS(app, resources={r"/*": {"origins": "*"}})


# Import the agent and tools from the previous code
# Assuming the previous code is saved in a file named 'book_agent.py'
from book_agent import graph

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query_agent():
    try:
        data = request.json
        user_message = data.get('message', '')
        
        # Prepare input for the agent
        inputs = {"messages": [("user", user_message)]}
        
        # Get response from agent
        responses = []
        for response in graph.stream(inputs, stream_mode="values"):
            message = response["messages"][-1]
            if isinstance(message, tuple):
                responses.append({
                    'role': message[0],
                    'content': message[1]
                })
            else:
                responses.append({
                    'role': 'assistant',
                    'content': message.content
                })
        
        return jsonify({'responses': responses})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add this section at the end of the file
if __name__ == '__main__':
    print("Starting Flask application...")
    # Run the Flask app with debug mode and make it accessible
    app.run(host='0.0.0.0', port=5000, debug=True)