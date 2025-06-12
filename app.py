from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Import agent with error handling
try:
    from book_agent import graph
    logger.info("Successfully imported book agent")
except Exception as e:
    logger.error(f"Failed to import book agent: {str(e)}")
    sys.exit(1)

@app.route('/')
def home():
    logger.info("Accessing home page")
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query_agent():
    try:
        logger.info("Received query request")
        data = request.json
        user_message = data.get('message', '')
        logger.info(f"Processing message: {user_message}")

        # Process with agent
        inputs = {"messages": [("user", user_message)]}
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
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({'error': str(e)}), 500

def main():
    try:
        # Verify environment variables
        required_vars = ["GOOGLE_API_KEY", "GOOGLE_CSE_ID", "OPENAI_API_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            sys.exit(1)
            
        logger.info("Starting Flask application...")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Failed to start Flask application: {str(e)}")
        raise

if __name__ == '__main__':
    main()