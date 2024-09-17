from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory
import google.generativeai as genai
import os
import requests

from stock_utils import get_stock_details

genai.configure(api_key=os.environ['gemapi'])


app = Flask(__name__)




@app.route('/', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def home():
    try:
        if request.method == 'POST':
            ticker = request.form.get('ticker').upper()
            return redirect(url_for('show_price', ticker=ticker))
        return render_template('home.html')
    except Exception as e:
        print(f"Error in home(): {str(e)}")  # This will print the specific error
        return f"An error occurred: {str(e)}", 500

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
                
                summary = response.text.replace('\n', '<br>')  

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

@app.route('/sentiment', methods=['GET', 'POST'])
def sentiment():
    if request.method == 'POST':
        ticker = request.form.get('ticker', '').upper()
        if ticker:
            url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&apikey=2E2UKJACTXKS62YA'
            r = requests.get(url)
            data = r.json()
            print(data)
            
            news_items = data.get('feed', [])
            
            processed_news = []
            for item in news_items:
                processed_item = {
                    'title': item['title'],
                    'url': item['url'],
                    'time_published': item['time_published'],
                    'summary': item['summary'],
                    'sentiment': item['overall_sentiment_label'],
                    'sentiment_score': item['overall_sentiment_score'],
                    'relevance_score': next((ts['relevance_score'] for ts in item['ticker_sentiment'] if ts['ticker'] == ticker), 'N/A')                }
                print(processed_item)
                processed_news.append(processed_item)
                
            
            return render_template('sentiment.html', news_items=processed_news, ticker=ticker)
    
    return render_template('sentiment.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/apple-touch-icon.png')
def apple_touch_icon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'apple-touch-icon.png', mimetype='image/png')

@app.route('/favicon-32x32.png')
def favicon_32():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon-32x32.png', mimetype='image/png')

@app.route('/favicon-16x16.png')
def favicon_16():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon-16x16.png', mimetype='image/png')

@app.route('/site.webmanifest')
def site_webmanifest():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'site.webmanifest', mimetype='application/json')


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)