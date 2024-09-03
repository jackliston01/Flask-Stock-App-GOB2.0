# stock_utils.py
import google.generativeai as genai
import os
import yfinance as yf

genai.configure(api_key=os.environ["gemapi"])

model = genai.GenerativeModel("gemini-1.5-flash")

def format_text(text):
    # Replace *word* with <strong>word</strong>
    while '*' in text:
        text = text.replace('*', '<strong>', 1)
        text = text.replace('*', '</strong>', 1)
    return text

def format_large_number(number):
    if number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.3f}B"
    elif number >= 1_000_000:
        return f"{number / 1_000_000:.3f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.3f}K"
    else:
        return f"{number:.3f}"

def get_stock_details(ticker):
    try:
        
        stock = yf.Ticker(ticker)
        info = stock.info
        
        if not info:
        
            return {'error': f"No information available for {ticker}"}
        
        current_price = info.get('regularMarketPrice', info.get('previousClose', 'N/A'))
        
        history = stock.history(period="5d")
        history_str = {str(date.date()): {k: round(v, 3) for k, v in row.items()} for date, row in history.iterrows()}
        
        dividends = stock.dividends
        
        dividends_str = {str(date.date()): round(div, 3) for date, div in dividends.items()}
        
        dividend_yield = info.get('dividendYield', 0)
        dividend_percentage = f"{round(dividend_yield * 100, 2)}%" if dividend_yield else 'N/A'

        news = stock.news if hasattr(stock, 'news') else []


        airesponse = model.generate_content(f'Summarize the company in 2 sentences using only objective language. Then provide an analysis of risk (audit risk. board risk, etc) using the actual concrete numbers provided. One sentence about performance using concrete numbers. And anything else UNIQUELY interesting given the info (must be objective and sourced from the info) This part should use some analysis {stock.info}')
        airesponse = airesponse.text
        airesponse = airesponse.replace('\n', '<br>')
        airesponse = format_text(airesponse)


        


        return {
            'ticker': ticker,
            'name': info.get('shortName', ticker),
            'current_price': f"{current_price:.3f}" if isinstance(current_price, (int, float)) else 'N/A',
            'day_high': f"{info.get('dayHigh', 'N/A'):.3f}" if info.get('dayHigh') else 'N/A',
            'day_low': f"{info.get('dayLow', 'N/A'):.3f}" if info.get('dayLow') else 'N/A',
            'open': f"{info.get('open', 'N/A'):.3f}" if info.get('open') else 'N/A',
            'previous_close': f"{info.get('previousClose', 'N/A'):.3f}" if info.get('previousClose') else 'N/A',
            'volume': f"{info.get('volume', 'N/A'):,}" if info.get('volume') else 'N/A',
            'market_cap': format_large_number(info.get('marketCap', 0)),
            'dividends': dividends_str,
            'history': history_str,
            'news': news,
            'dividend': dividend_percentage,
            'ai_response': airesponse
        }
    except Exception as e:
    
     
        return {'error': f"Unable to fetch stock details for {ticker}"}