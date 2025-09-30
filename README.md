# Message Generator Feature

A **web-based Greeting Message Generator** built with **Flask**, designed to create personalized messages for customers quickly and easily. This project combines **rule-based templates** for common occasions like Diwali, New Year, and birthdays, with **AI-powered message generation** using the Hugging Face API. Users can select a tone—Formal, Friendly, or Festive—so messages feel professional, approachable, or celebratory.

## Features

- **Rule-based templates** for popular occasions.
- **AI-powered message generation** via Hugging Face.
- Selectable **message tone**: Formal, Friendly, Festive.
- **Customer name input** for personalized greetings.
- **Responsive and user-friendly interface** using HTML, CSS, and JavaScript.
- Automatic fallback to rule-based messages if AI service is unavailable.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Ayush-Awasthi01/message-generator-feature.git
    cd message-generator-feature
    ```

2. Create and activate a virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3. Install required packages:

    ```bash
    pip install -r requirements.txt
    ```

4. Set your Hugging Face API key:

    ```bash
    setx HUGGINGFACE_API_KEY "your_hf_api_key_here"
    ```

## Usage

1. Run the Flask app:

    ```bash
    python app.py
    ```

2. Open your browser and navigate to:

    ```
    http://127.0.0.1:5000
    ```

3. Enter a prompt, optionally a customer name, select tone, and click **Generate**.

## Technologies Used

- **Flask** – Backend framework
- **HTML, CSS, JavaScript** – Frontend
- **Pillow (PIL)** – Image handling
- **Requests** – API calls
- **Hugging Face API** – AI-powered message generation

## Notes

- AI service requires a valid Hugging Face API key.
- Rule-based messages are used as fallback if AI service is unavailable.
- Images and messages are dynamically generated and displayed on the page.

---

This project is ideal for **small businesses or customer service teams** looking to send personalized greetings efficiently, combining practical AI usage with a lightweight web application.
