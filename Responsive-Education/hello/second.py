from flask import Flask, render_template, request, jsonify, Blueprint
from groq import Groq

app = Flask(__name__)

# Create a Blueprint
second_bp = Blueprint('second', __name__, template_folder='templates')

# Initialize the Groq client with the API key
client = Groq(api_key="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")

# Function to limit words in a string
def limit_words(text, max_words=50):
    words = text.split()
    if len(words) <= max_words:
        return text
    return ' '.join(words[:max_words]) + '...'

# Route within the Blueprint
@second_bp.route('/chat1')
def chat1():
    return render_template('chatbot.html')

@second_bp.route('/chat', methods=['POST'])
def chat():
    user_input = request.form.get('user_input')
    
    if not user_input:
        return jsonify({'response': 'Please provide some input.'})
    
    try:
        # Create chat completion request
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": user_input}
            ],
            model="llama3-8b-8192",
            max_tokens=150  # Limit the response length from the API
        )

        # Extract the response from the API
        if chat_completion.choices:
            response = chat_completion.choices[0].message.content
            limited_response = limit_words(response, max_words=50)  # Limit to 50 words
            return jsonify({'response': limited_response})
        else:
            return jsonify({'response': 'Error generating response. Please try again.'})
    
    except Exception as e:
        # Log any exceptions that occur
        print(f"Error: {str(e)}")
        return jsonify({'response': f"An error occurred: {str(e)}"})

# Register the Blueprint with the app
app.register_blueprint(second_bp, url_prefix='/second')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')