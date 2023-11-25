from flask import Flask, render_template, request, redirect, send_file, url_for, flash
import PyPDF2
import pdfplumber
import fitz  # PyMuPDF (MuPDF)
from gtts import gTTS
from googletrans import Translator
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')



# Function to extract text from a PDF using PyPDF2
def extract_text_pyPDF2(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
        return text
    except Exception as e:
        flash(f"PyPDF2 PDF text extraction failed: {str(e)}")
        return None

# Function to extract text from a PDF using pdfplumber
def extract_text_pdfplumber(pdf_file):
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                text += page_text
            return text
    except Exception as e:
        flash(f"pdfplumber PDF text extraction failed: {str(e)}")
        return None

# Function to extract text from a PDF using PyMuPDF (MuPDF)
def extract_text_PyMuPDF(pdf_file):
    try:
        text = ""
        pdf_document = fitz.open(pdf_file)
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            text += page.get_text()
        pdf_document.close()
        return text
    except Exception as e:
        flash(f"PyMuPDF PDF text extraction failed: {str(e)}")
        return None


# Function to translate text
def translate_text(text, target_language):
    try:
        translator = Translator()
        translated_text = translator.translate(text, dest=target_language)
        return translated_text.text
    except Exception as e:
        flash(f"Translation failed: {str(e)}")
        return None

# Function to convert text to speech and save as an MP3 file
def convert_text_to_speech(text):
    try:
        speech = gTTS(text)
        speech.save("output.mp3")
        return "output.mp3"
    except Exception as e:
        flash(f"Text-to-speech conversion failed: {str(e)}")
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pdf_file = request.files["pdf"]
        
        target_language = request.form["target_language"]
        text = None

        if pdf_file:
            # Try different PDF extraction methods until one succeeds
            text = extract_text_pyPDF2(pdf_file) or \
                   extract_text_pdfplumber(pdf_file) or \
                   extract_text_PyMuPDF(pdf_file)



        if text:
            translated_text = translate_text(text, target_language)
            if translated_text:
                speech = convert_text_to_speech(translated_text)
                if speech:
                    return redirect(url_for("play_speech"))

    return render_template("index.html")

@app.route("/play_speech")
def play_speech():
    return send_file("output.mp3")

if __name__ == "__main__":
    app.run(debug=True)