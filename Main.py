import tkinter as tk
from tkinter import ttk
import requests
import json
import os
from datetime import datetime

API_KEY = "5fba68ca61fd36e06d475d8c665fc21d"
BASE_URL = f"http://data.fixer.io/api/latest?access_key={API_KEY}&symbols=USD,INR,GBP,JPY,EUR"
JSON_FILE = "exchange_rates.json"

class CurrencyConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        
        # Load exchange rate data
        self.data = self.initialize_rates()
        
        # UI elements
        self.amount_label = tk.Label(root, text="Amount:")
        self.amount_label.grid(row=0, column=0, padx=30, pady=10)
        
        self.amount_entry = tk.Entry(root)
        self.amount_entry.grid(row=0, column=1, padx=10, pady=10)
        
        self.from_currency_label = tk.Label(root, text="From:")
        self.from_currency_label.grid(row=1, column=0, padx=30, pady=10)
        
        self.from_currency = ttk.Combobox(root, values=["EUR", "USD", "INR", "GBP", "JPY"])
        self.from_currency.grid(row=1, column=1, padx=10, pady=10)
        self.from_currency.set("USD")
        
        self.to_currency_label = tk.Label(root, text="To:")
        self.to_currency_label.grid(row=2, column=0, padx=30, pady=10)
        
        self.to_currency = ttk.Combobox(root, values=["EUR", "USD", "INR", "GBP", "JPY"])
        self.to_currency.grid(row=2, column=1, padx=10, pady=10)
        self.to_currency.set("INR")
        
        self.convert_button = tk.Button(root, text="Convert", command=self.convert)
        self.convert_button.grid(row=3, column=0, columnspan=2, pady=20)
        
        self.result_label = tk.Label(root, text="Converted Amount: ")
        self.result_label.grid(row=4, column=0, columnspan=2, pady=10)
        

        timestamp = self.format_timestamp(self.data.get("timestamp", "N/A"))
        self.timestamp_label = tk.Label(root, text=f"Last Updated: {timestamp}")
        self.timestamp_label.grid(row=5, column=0, columnspan=2, pady=10)

    def is_connected(self):
        try:
            requests.get("https://www.google.com/", timeout=5)
            return True
        except requests.ConnectionError:
            return False

    def fetch_exchange_rates(self):
        response = requests.get(BASE_URL)
        data = response.json()
        
        if data.get("success"):
            data["timestamp"] = datetime.now().isoformat() 
            with open(JSON_FILE, 'w') as file:
                json.dump(data, file) 
            return data
        else:
            return None

    def load_exchange_rates(self):
        with open(JSON_FILE, 'r') as file:
            return json.load(file)

    def initialize_rates(self):
        if self.is_connected():
            print("Connected to the internet. Fetching latest exchange rates...")
            data = self.fetch_exchange_rates()
            if data:
                return data
            else:
                print("Error: Failed to fetch data from the API.")
                exit()
        elif os.path.exists(JSON_FILE):
            print("No internet connection. Loading saved exchange rates...")
            return self.load_exchange_rates()
        else:
            print("No data available and no internet connection. Exiting.")
            exit()

    def fetch_rate(self, from_currency, to_currency):
        rates = self.data.get("rates", {})
        if from_currency == "EUR":
            return rates.get(to_currency)
        elif to_currency == "EUR":
            return 1 / rates.get(from_currency)
        else:
            rate_from_currency = rates.get(from_currency)
            rate_to_currency = rates.get(to_currency)
            if rate_from_currency and rate_to_currency:
                return rate_to_currency / rate_from_currency
            else:
                return None

    def convert(self):
        try:
            amount = float(self.amount_entry.get())
            from_currency = self.from_currency.get()
            to_currency = self.to_currency.get()
            rate = self.fetch_rate(from_currency, to_currency)
            if rate:
                converted_amount = amount * rate
                self.result_label.config(text=f"Converted Amount: {converted_amount:.2f} {to_currency}")
            else:
                self.result_label.config(text="Error fetching conversion rate.")
        except ValueError:
            self.result_label.config(text="Please enter a valid amount.")
    
    def format_timestamp(self, timestamp):
        try:
            dt = datetime.fromisoformat(timestamp)
            return dt.strftime("%d-%m-%Y %I:%M %p")
        except ValueError:
            return "N/A"

# Create the main window and run the application
root = tk.Tk()
app = CurrencyConverterApp(root)
root.mainloop()
