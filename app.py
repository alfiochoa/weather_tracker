import requests
import pandas as pd
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone



#Api key
weather_api_key =  '5d11350da0d644d6916162855252604'

#list of cities
cities = ['Madrid', 'New York', 'Tampa','London']
days= 3

weather_data = []
errors = []

for city in cities:
    #base url for weather api
    url = f'https://api.weatherapi.com/v1/forecast.json?key={weather_api_key}&q={city}&days={days}&aqi=no&alerts=no'
    #send the GET request
    try:
        response = requests.get(url)

    #check if the call was successful
        if response.status_code == 200:
        #parse JSON response
            data = response.json()
        #extract relevant information from the data
            try:
                region = data['location']['region']
                country = data['location']['country']
                localtime = data['location']['localtime']
                record_time = localtime[:13] + ":00"
                temp = data['current']['temp_c']
                humidity = data['current']['humidity']
                condition = data ['current']['condition']['text']
                condition_icon = data['current']['condition']['icon']
                feelslike_c = data['current']['feelslike_c']
                wind_kph = data['current']['wind_kph']
                cloud = data['current']['cloud']
                maxtemp_c = data['forecast']['forecastday'][0]['day']['maxtemp_c']
                mintemp_c = data['forecast']['forecastday'][0]['day']['mintemp_c']
                daily_will_it_rain = data['forecast']['forecastday'][0]['day']['daily_will_it_rain']
                daily_chance_of_rain = data['forecast']['forecastday'][0]['day']['daily_chance_of_rain']
                daily_will_it_snow = data['forecast']['forecastday'][0]['day']['daily_will_it_snow']
                daily_chance_of_snow = data['forecast']['forecastday'][0]['day']['daily_chance_of_snow']
                sunrise = data['forecast']['forecastday'][1]['astro']['sunrise']
                sunset = data['forecast']['forecastday'][1]['astro']['sunset']
                moon_phase = data['forecast']['forecastday'][1]['astro']['moon_phase']

        #append the data to weather_data list
                weather_data.append({
                    'city':city,
                    'region':region,
                    'country':country,
                    'temperature':temp,
                    'local_time':localtime,
                    'record_time':record_time,
                    'feels_like': feelslike_c,
                    'max_temp': maxtemp_c,
                    'min_temp': mintemp_c,
                    'humidity':humidity,
                    'condition':condition,
                    #'Condition': condition_icon,
                    'local_time': localtime,
                    'wind':wind_kph,
                    'cloud':cloud,
                    'sunrise': sunrise,
                    'sunset': sunset,
                    'moon_phase':moon_phase,
                    'chance_of_rain':daily_chance_of_rain,
                    'chance_of_snow':daily_chance_of_snow
                    })


            except (KeyError, TypeError, IndexError) as e:
                print(f"⚠️ {type(e).__name__} for {city} → {e}")
                errors.append({
                'city': city,
                'Status Code': response.status_code,
                'Error': f"{type(e).__name__}: {e}"
             })


        elif response.status_code == 400:
            print(f"Bad request for {city}\n")
            errors.append({'City':city, 'Status Code': 400, 'Error':'Bad Request'})

        elif response.status_code == 401:
            print(f"Unauthorized! Check your API Key\n")
            errors.append({'City':city, 'Status Code': 401, 'Error':'Unauthorized'})

        elif response.status_code == 403:
            print(f"Forbidden request for {city}\n")
            errors.append({'City':city, 'Status Code': 403, 'Error':'Forbidden'})

        elif response.status_code == 404:
            print(f"{city} city not found!\n")
            errors.append({'City':city, 'Status Code': 404, 'Error':'Not Found'})
        else:
            print(f"Error fetching data for {city}: Status {response.status_code}\n")
            errors.append({'City':city,'Status Code':response.status_code, 'Error':'Other'})
    except requests.exceptions.RequestException as e:
        print(f"request exception for {city}: {e}")
        errors.append({'City':city, 'Status Code':'N/A','Error':str(e)})
    


# Create DataFrames
df_weather = pd.DataFrame(weather_data)
df_errors = pd.DataFrame(errors)



#display the data frame
print(df_weather)


if not df_errors.empty:
    print("\nErrors encountered:")
    print(df_errors)
#convert data frame into dictionary to be inserted to the DB
df_weather_dict = df_weather.to_dict(orient='records')


#start the supabase client
load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# Function to authenticate user
def authenticate_user(email: str, password: str):
    return supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

email: str = os.environ.get("SUPABASE_EMAIL")
password: str = os.environ.get("SUPABASE_PASSWORD")

auth_response = authenticate_user(email, password)

if auth_response.user:
    print(f"✅ Authenticated: {auth_response.user.email}")
else:
    print("❌ Authentication failed.")


cutoff = datetime.now(timezone.utc) - timedelta(days=2)

# delete query to avoid going over supabase size limit
response = supabase.table("weather_logs").delete().lt("created_at", cutoff.isoformat()).execute()

print(f"Deleted old entries count:\n{response}")


#Checking for duplicates and inserting data
response = supabase.table("weather_logs") \
    .select("*") \
    .eq('city', city) \
    .eq('record_time', record_time) \
    .execute()


if not response.data:  
    insert_response = supabase.table("weather_logs").insert(df_weather_dict).execute()
    for city in df_weather_dict:
        print(f"Data inserted for {city} at {record_time}")
else:
    print(f"Duplicate values found for {city} at {record_time}. Skipping insertion.")