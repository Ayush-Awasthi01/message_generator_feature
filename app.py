from flask import Flask, render_template, request, jsonify
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = os.getenv("HF_MODEL")
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

# Rule-based templates
TEMPLATES = {
    "diwali": "Hello {name}, Diwali greetings! Wishing you a prosperous and joyful holiday season.",
    "new year": "Dear {name}, Happy New Year! Wishing you success, health, and happiness in the year ahead.",
    "birthday": "Dear {name}, wishing you a very Happy Birthday! May your day be filled with joy and celebration."
}

# --- Helper: call Hugging Face API ---
def generate_ai_message(prompt, name, style="Formal"):
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    data = {
        "inputs": f"Write a {style} message for the following prompt: {prompt}. Address the customer as {name}.",
        "parameters": {"max_new_tokens": 150}
    }
    response = requests.post(HF_API_URL, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]
        return "AI response could not be parsed."
    else:
        print("HF API returned status:", response.status_code)
        return None

# --- Routes ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate_message", methods=["POST"])
def generate_message():
    data = request.get_json()
    prompt = data.get("prompt", "")
    mode = data.get("mode", "rule")
    name = data.get("name", "Customer")
    style = data.get("style", "Formal")

    # --- Rule-based ---
    if mode == "rule":
        for key, template in TEMPLATES.items():
            if key.lower() in prompt.lower():
                return jsonify({"message": template.format(name=name)})
        return jsonify({"message": f"Dear {name}, thank you for reaching out. {prompt}"})

    # --- AI-powered ---
    elif mode == "llm":
        ai_message = generate_ai_message(prompt, name, style)
        if ai_message:
            return jsonify({"message": ai_message})
        else:
            # fallback to rule-based
            for key, template in TEMPLATES.items():
                if key.lower() in prompt.lower():
                    return jsonify({"message": template.format(name=name)})
            return jsonify({"message": f"Dear {name}, thank you for reaching out. {prompt}"})

    return jsonify({"error": "Invalid mode"}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
