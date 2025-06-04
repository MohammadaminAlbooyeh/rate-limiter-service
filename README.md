# 💱 Currency Converter App

This is a simple and interactive **currency converter** built with **Python** and **Streamlit**. It allows users to convert an amount from one currency to another using real-time exchange rates from [ExchangeRate-API](https://www.exchangerate-api.com/).

---

## 🚀 Features

* Convert between any two currencies.
* Real-time exchange rates.
* Clean and responsive Streamlit UI.
* Flashing arrow animation to highlight currency flow.
* Easy to use and mobile-friendly.

---

## 📦 Requirements

* Python 3.7+
* [Streamlit](https://streamlit.io/)
* [requests](https://pypi.org/project/requests/)

---

## 🔧 Installation

1. **Clone the repository:**

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Run the app:**

```bash
streamlit run app.py
```

---

## 🧠 How It Works

* Select the base currency and target currency from dropdowns.
* Enter the amount you want to convert.
* The app fetches the latest exchange rate using `get_exchange_rate()` and performs the conversion using `convert_currency()` from helper modules.
* Results are displayed with visual indicators and an animated arrow for a better user experience.

---

## 🗃️ Project Structure

```
🔹 app.py                  # Main Streamlit app
🔹 constants.py            # List of supported currencies
🔹 currency_convertor.py   # Functions for getting rates and conversion
🔹 requirements.txt        # Python dependencies
🔹 README.md               # Project documentation
```

---

## 🌐 API Source

This app uses [ExchangeRate-API](https://www.exchangerate-api.com/) to get up-to-date exchange rates between currencies.

---

## 🙌 Acknowledgements

* [Streamlit](https://streamlit.io/)
* [ExchangeRate-API](https://www.exchangerate-api.com/)
