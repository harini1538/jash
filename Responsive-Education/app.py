from flask import Flask, render_template,Blueprint

from hello.second import second_bp
from hello.third import third_bp
from hello.four import four_bp

app = Flask(__name__)

# Register the Blueprints
app.register_blueprint(second_bp, url_prefix='/second')
app.register_blueprint(third_bp, url_prefix='/third')
app.register_blueprint(four_bp, url_prefix='/four')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
