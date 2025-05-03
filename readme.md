# 🌦️ Weather Tracker

A Python-based weather tracking pipeline that collects hourly weather data for multiple cities and stores it in a Supabase database — perfect for portfolio projects or data analytics!

---

## 🚀 Features

- Fetches real-time weather data via API
- Cleans and processes the data with pandas
- Avoids duplicates by checking timestamps
- Uploads records to a Supabase cloud database
- Error-handled and ready for automation (hourly updates)

---

## 📦 Built With

- Python
- Supabase
- requests
- pandas
- dotenv

---

## 🔐 Environment Variables

Create a `.env` file with the following:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_EMAIL=your_registered_email
SUPABASE_PASSWORD=your_password
