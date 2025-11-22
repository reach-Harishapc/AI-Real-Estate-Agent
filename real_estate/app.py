from flask import Flask, render_template, request, jsonify
from main import agent_executor
import markdown

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        # Invoke the agent
        response = agent_executor.invoke({"input": user_message})
        output = response['output']
        
        # Convert Markdown to HTML for better display
        output_html = markdown.markdown(output)
        
        return jsonify({'response': output_html})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
