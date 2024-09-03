from flask import Flask, request, render_template, redirect, url_for, flash


from stock_utils import get_stock_details



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

@app.route('/docanalysis')
def docanalysis():
    return render_template('docanalysis.html')


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


