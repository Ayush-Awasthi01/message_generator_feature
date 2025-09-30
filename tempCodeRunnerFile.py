from flask import Flask, render_template, request, jsonify, url_for
import os
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

app = Flask(__name__)

# Initialize OpenAI client if available
if OPENAI_AVAILABLE:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Rule-based templates
TEMPLATES = {
    "diwali": {
        "text": "Hello {name}, Diwali greetings! We wish you a prosperous and joyful holiday season.",
        "image": "diwali.jpg"
    },
    "new year": {
        "text": "Dear {name}, Happy New Year! Wishing you success, health, and happiness in the year ahead.",
        "image": "newyear.jpg"
    },
    "birthday": {
        "text": "Dear {name}, wishing you a very Happy Birthday! May your day be filled with joy and celebration.",
        "image": "birthday.jpg"
    }
}

# --- Helper: add diagonal semi-transparent watermark ---
def add_watermark(image, text="Ayush", font_path="static/fonts/Poppins-Bold.ttf"):
    watermark = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)

    try:
        font_size = int(min(image.size) / 10)
        font = ImageFont.truetype(font_path, font_size)
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    textwidth = bbox[2] - bbox[0]
    textheight = bbox[3] - bbox[1]

    x = (image.width - textwidth) // 2
    y = (image.height - textheight) // 2

    draw.text((x, y), text, font=font, fill=(255, 255, 255, 100))
    watermark = watermark.rotate(30, expand=1)
    watermarked = Image.alpha_composite(image.convert("RGBA"), watermark)
    return watermarked.convert("RGB")

# --- Helper: save AI-generated image locally with watermark ---
def save_ai_image(url, filename="generated.jpg"):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content)).convert("RGB")
        watermarked = add_watermark(img)
        save_path = os.path.join("static", filename)
        watermarked.save(save_path, "JPEG")
        return url_for('static', filename=filename)
    except Exception:
        return url_for('static', filename="default.jpg")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_message', methods=['POST'])
def generate_message():
    data = request.get_json()
    prompt = data.get("prompt", "")
    mode = data.get("mode", "rule")
    name = data.get("name", "Customer")
    style = data.get("style", "Formal")

    # --- Rule-based messages ---
    if mode == "rule":
        prompt_lower = prompt.lower()
        for key, template in TEMPLATES.items():
            if key in prompt_lower:
                img_path = os.path.join("static", template["image"])
                try:
                    img = Image.open(img_path).convert("RGB")
                    watermarked = add_watermark(img)
                    watermarked.save(img_path)
                except Exception:
                    pass  # fallback silently
                return jsonify({
                    "message": template["text"].format(name=name),
                    "image_url": url_for('static', filename=template["image"])
                })
        # Fallback for unmatched prompts
        return jsonify({
            "message": f"Dear {name}, thank you for reaching out. {prompt}",
            "image_url": url_for('static', filename="default.jpg")
        })

    # --- LLM / AI-powered messages ---
    elif mode == "llm" and OPENAI_AVAILABLE:
        try:
            # Generate professional message
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": (
                        f"You are a professional communication assistant. "
                        f"Generate polished, customer-friendly messages in a {style} tone. "
                        "Keep messages clear, positive, and appropriate for business or customer communication."
                    )},
                    {"role": "user", "content": f"Prompt: {prompt}. Address the customer as {name}."}
                ]
            )
            message = response.choices[0].message.content

            # Try AI image
            try:
                image_prompt = f"{prompt}, professional festive greeting card design"
                image_response = client.images.generate(
                    model="gpt-image-1",
                    prompt=image_prompt,
                    size="512x512"
                )
                image_url = save_ai_image(image_response.data[0].url)
            except Exception:
                # fallback to default/static
                fallback = "default.jpg"
                for key, template in TEMPLATES.items():
                    if key in prompt.lower():
                        fallback = template["image"]
                        break
                fallback_path = os.path.join("static", fallback)
                try:
                    img = Image.open(fallback_path).convert("RGB")
                    watermarked = add_watermark(img)
                    watermarked.save(fallback_path)
                except Exception:
                    pass
                image_url = url_for('static', filename=fallback)

            return jsonify({"message": message, "image_url": image_url})

        except Exception as e:
            return jsonify({
                "error": f"AI service unavailable. Using rule-based fallback. ({str(e)})",
                "message": f"Dear {name}, thank you for reaching out. {prompt}",
                "image_url": url_for('static', filename="default.jpg")
            })

    # --- Fallback for invalid mode ---
    return jsonify({
        "error": "Invalid mode. Please select 'rule' or 'llm'.",
        "message": f"Dear {name}, thank you for reaching out. {prompt}",
        "image_url": url_for('static', filename="default.jpg")
    })

if __name__ == '__main__':
    app.run(debug=True)
