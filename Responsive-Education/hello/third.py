from flask import Flask, render_template, request, jsonify,Blueprint
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
third_bp = Blueprint('third', __name__, template_folder='templates')

QUESTIONS = [
    "How often do you feel anxious or worried about your future?",
    "Do you frequently feel overwhelmed by your daily responsibilities?",
    "How often do you find yourself feeling sad or down without a clear reason?",
    "Do you struggle to concentrate or focus on tasks?",
    "How often do you feel like you have no control over your life?",
    "Do you feel isolated or disconnected from others?",
    "How often do you have difficulty sleeping due to racing thoughts?",
    "Do you find it hard to enjoy activities you used to like?",
    "How frequently do you experience physical symptoms like headaches or stomachaches due to stress?",
    "Do you find it challenging to manage your emotions in stressful situations?"
]

MOOD_MAPPING = {
    "sorrow": 0,
    "sad": 1,
    "neutral": 2,
    "normal": 3,
    "happy": 4
}

def predict_stress_level(answers):
    # Convert text answers to numerical values
    numerical_answers = [MOOD_MAPPING.get(answer, 2) for answer in answers]
    stress_level = np.mean(numerical_answers) / 4.0  # Normalize to 0-1 range
    return stress_level


@third_bp.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        answers = [request.form.get(f'q{i}') for i in range(len(QUESTIONS))]
        stress_level = predict_stress_level(answers)
        
        # Simulate stress level data for demonstration
        predicted_stress_levels = np.random.uniform(0, 1, 10)
        colors = ['green' if level < 0.33 else 'yellow' if level < 0.66 else 'red' for level in predicted_stress_levels]
        
        # Plotting the scaling concept
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(range(1, 11), predicted_stress_levels, color=colors)
        ax.set_title('Stress Level Analysis', fontsize=16, fontweight='bold')
        ax.set_xlabel('Sample', fontsize=14)
        ax.set_ylabel('Predicted Stress Level', fontsize=14)
        ax.set_ylim(0, 1)
        ax.set_xticks(range(1, 11))
        ax.set_xticklabels([f'Sample {i+1}' for i in range(10)])
        
        import matplotlib.patches as mpatches
        low_patch = mpatches.Patch(color='green', label='Low Stress')
        medium_patch = mpatches.Patch(color='yellow', label='Moderate Stress')
        high_patch = mpatches.Patch(color='red', label='High Stress')
        ax.legend(handles=[low_patch, medium_patch, high_patch])
        
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()

        return jsonify({'plot_url': plot_url})

    return render_template('stress.html', questions=QUESTIONS)

if __name__ == '__main__':
    app.run(debug=True)
