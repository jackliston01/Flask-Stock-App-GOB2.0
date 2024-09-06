from flask import Flask, request, render_template, redirect, url_for, flash
import google.generativeai as genai
import os

from stock_utils import get_stock_details

genai.configure(api_key=os.environ['gemapi'])


app = Flask(__name__)




@app.route('/', methods=['GET', 'POST'])
def home():
    try:
        if request.method == 'POST':
            ticker = request.form.get('ticker').upper()
            return redirect(url_for('show_price', ticker=ticker))
        return render_template('home.html')
    except Exception as e:
        return "An error occurred", 500

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/docanalysis', methods=['GET', 'POST'])
def docanalysis():
    summary = None

    if request.method == 'POST':
        file = request.files['file']
        if file:
            file.save(file.filename)
            
            try:
                sample_file = genai.upload_file(path=file.filename, display_name="Gemini PDF")
                
                model = genai.GenerativeModel(model_name="gemini-1.5-flash")
                response = model.generate_content([sample_file, "Can you summarize this document as a bulleted list?"])
                
                summary = response.text.replace('\n', '<br>')  # Convert newlines to HTML line breaks

            except Exception as e:
                summary = f"An error occurred: {str(e)}"

    return render_template('docanalysis.html', summary=summary)
@app.route('/<ticker>')
def show_price(ticker):
    stock_data = get_stock_details(ticker)
    print(f"Stock data for {ticker}: {stock_data}")  # For debugging
    return render_template('stock_details.html', 
                           stock_data=stock_data, 
                           news=stock_data.get('news', []),
                           history=stock_data.get('history', {}))

@app.route('/favicon.ico')
def favicon():
    return '', 204


