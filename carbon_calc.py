from flask import Flask, render_template, request, redirect, url_for, make_response
import json
from models.food_source import FoodSource
from models.transport import Transport
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# =====================
# FoodSource Routes
# =====================
@app.route('/food', methods=['GET', 'POST'])
def food_page():
    if request.method == 'POST':
        # Gunakan sector_id yang tetap untuk sektor "food"
        SECTOR_ID_FOOD = 1  # Asumsikan sektor food memiliki ID 1

        food = FoodSource(
            sector_name='food',
            food_id=request.form['food_id'],
            name_en=request.form['name_en'],
            name_id=request.form['name_id'],
            unit=request.form['unit'],
            emisi=float(request.form['emisi'])
        )

        # Overwrite sektor ID-nya dengan yang sudah fix
        food.sector_id = SECTOR_ID_FOOD

        # Langsung insert ke food saja
        supabase.table("food").insert(food.to_dict()).execute()

        return redirect(url_for('food_page'))

    data = supabase.table("food").select("*").execute().data
    return render_template('food.html', data=data)



# =====================
# Transport Routes
# =====================
@app.route('/transport', methods=['GET', 'POST'])
def transport_page():
    if request.method == 'POST':
        SECTOR_ID_TRANSPORT = 2  # Asumsikan transport memiliki ID 2

        transport = Transport(
            sector_name='transport',
            category=request.form['category'],
            transport_id=request.form['transport_id'],
            name_en=request.form['name_en'],
            name_id=request.form['name_id'],
            unit=request.form['unit'],
            emisi=float(request.form['emisi'])
        )

        transport.sector_id = SECTOR_ID_TRANSPORT

        supabase.table("transport").insert(transport.to_dict()).execute()

        return redirect(url_for('transport_page'))

    data = supabase.table("transport").select("*").execute().data
    return render_template('transport.html', data=data)


# =====================
# Sector Routes
# =====================
@app.route('/sector', methods=['GET', 'POST'])
def sector_page():
    if request.method == 'POST':
        from models.sector import Sector
        sector = Sector(sector_name=request.form['sector_name'])
        supabase.table("sector").insert(sector.to_dict()).execute()
        return redirect(url_for('sector_page'))

    data = supabase.table("sector").select("*").order("sector_id").execute().data
    return render_template('sector.html', data=data)

# =====================
# Emission Calculator
# =====================
@app.route('/calculate', methods=['GET', 'POST'])
def calculate_emission():
    result = None
    selected_sector = request.form.get('sector') if request.method == 'POST' else request.cookies.get('selected_sector')
    selected_id = None
    amount = None

    # Ambil data dari Supabase
    foods = supabase.table("food").select("*").execute().data
    transports = supabase.table("transport").select("*").execute().data

    # Ambil riwayat dari cookie
    cookie_history = request.cookies.get("emission_history")
    history = json.loads(cookie_history) if cookie_history else []

    # Pilih entitas berdasarkan sektor
    entities = []
    if selected_sector == 'food':
        entities = foods
    elif selected_sector == 'transport':
        entities = transports

    if request.method == 'POST':
        selected_id = request.form.get('item_id')
        amount_raw = request.form.get('amount')

        if selected_id and amount_raw:
            amount = float(amount_raw)
            entity = next((item for item in entities if item['id'] == selected_id), None)

            if entity:
                result = {
                    "name_id": entity["name_id"],
                    "unit": entity["unit"],
                    "emisi": entity["emisi"],
                    "amount": amount,
                    "total_emission": round(amount * entity["emisi"], 4)
                }
                history.append(result)

                total_emission_sum = round(sum(item['total_emission'] for item in history), 4)

                response = make_response(render_template(
                    "calc.html",
                    foods=foods,
                    transports=transports,
                    entities=entities,
                    result=result,
                    selected_sector=selected_sector,
                    selected_id=selected_id,
                    amount=amount,
                    history=history,
                    total_emission_sum=total_emission_sum
                ))
                response.set_cookie("emission_history", json.dumps(history))
                response.set_cookie("selected_sector", selected_sector)
                return response

    total_emission_sum = round(sum(item['total_emission'] for item in history), 4)
    return render_template("calc.html",
                           foods=foods,
                           transports=transports,
                           entities=entities,
                           result=result,
                           selected_sector=selected_sector,
                           selected_id=selected_id,
                           amount=amount,
                           history=history,
                           total_emission_sum=total_emission_sum)

# =====================
# Reset History
# =====================
@app.route('/reset-history', methods=['POST'])
def reset_history():
    response = make_response(redirect(url_for('calculate_emission')))
    response.set_cookie("emission_history", '', expires=0)
    response.set_cookie("selected_sector", '', expires=0)
    return response
    return response


if __name__ == '__main__':
    app.run(debug=True)
