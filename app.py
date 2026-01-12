from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import numpy as np
import pickle
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = "secret_cbl_123"

# 1. LOAD MODEL
# Pastikan file prediksi.pkl ada di folder yang sama dengan app.py
with open("prediksi.pkl", "rb") as f:
    model = pickle.load(f)

# 2. KONFIGURASI DATABASE
DB_CONFIG = {
    "host": os.environ.get("DB_HOST"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "database": os.environ.get("DB_NAME"),
    "port": int(os.environ.get("DB_PORT", 3306))
}

VALID_USERNAME = "admin"
VALID_PASSWORD = "admin123"

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"Error Database: {err}")
        return None

def generate_health_advice(data, status):
    advice_list = []

    # Hitung BMI
    bmi = data["Weight"] / (data["Height"] ** 2)

    if status != "Normal":
        advice_list.append("Kurangi konsumsi makanan tinggi kalori, gula, dan lemak jenuh.")
        advice_list.append("Tingkatkan aktivitas fisik secara bertahap minimal 150 menit per minggu.")
        advice_list.append("Atur pola makan dengan porsi seimbang dan jadwal teratur.")

        if bmi >= 30:
            advice_list.append("Disarankan konsultasi dengan tenaga kesehatan atau ahli gizi.")

    else:
        advice_list.append("Pertahankan pola makan sehat dan seimbang.")
        advice_list.append("Lanjutkan kebiasaan olahraga rutin untuk menjaga kebugaran.")

    # Air minum
    if data["CH2O"] < 2:
        advice_list.append("Tingkatkan konsumsi air putih minimal 2 liter per hari.")

    # Aktivitas fisik
    if data["FAF"] < 1:
        advice_list.append("Tambahkan aktivitas fisik ringan seperti jalan kaki atau peregangan.")

    # Waktu layar
    if data["TUE"] > 4:
        advice_list.append("Kurangi waktu penggunaan gadget dan perbanyak aktivitas fisik.")

    # Sayur
    if data["FCVC"] < 2:
        advice_list.append("Perbanyak konsumsi sayur dan buah setiap hari.")

    return advice_list

# 3. ROUTE LOGIN
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("questionnaire"))
        else:
            return render_template("login.html", error="Username atau Password salah!")
    return render_template("login.html")

# 4. ROUTE QUESTIONNAIRE & PREDIKSI
@app.route("/questionnaire", methods=["GET", "POST"])
def questionnaire():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            # 1. Ambil data identitas
            no_rm = request.form.get("no_rekam_medis")
            nama_pasien = request.form.get("nama_pasien")

            # 2. Persiapkan data untuk model
            data = {
                "Gender": request.form.get("Gender"),
                "Age": float(request.form.get("Age")),
                "Height": float(request.form.get("Height")),
                "Weight": float(request.form.get("Weight")),
                "family_history_with_overweight": int(request.form.get("family_history_with_overweight")),
                "FAVC": int(request.form.get("FAVC")),
                "FCVC": float(request.form.get("FCVC")),
                "NCP": float(request.form.get("NCP")),
                "CAEC": request.form.get("CAEC"),
                "SMOKE": int(request.form.get("SMOKE")),
                "CH2O": float(request.form.get("CH2O")),
                "SCC": int(request.form.get("SCC")),
                "FAF": float(request.form.get("FAF")),
                "TUE": float(request.form.get("TUE")),
                "CALC": request.form.get("CALC"),
                "MTRANS": request.form.get("MTRANS"),
            }

            df_input = pd.DataFrame([data])

            # 3. Prediksi Model
            y_pred = model.predict(df_input)[0]
            
            # PAKSA KONVERSI: Pastikan status menjadi string Python biasa
            # Jika y_pred bernilai 0/1 (int64), kita ubah ke teks
            if str(y_pred) == '1' or y_pred == 'Obesity_Type_I' or 'Overweight' in str(y_pred):
                status = "Beresiko Obesitas"
            else:
                status = "Normal"

            # Generate advice otomatis
            advice_list = generate_health_advice(data, status)


            # Ambil probabilitas dan paksa ke float Python biasa
            try:
                raw_proba = model.predict_proba(df_input)[0].max()
                proba = float(raw_proba) 
            except:
                proba = 1.0

            # 4. Fitur Penting (Top Factors)
            # Pastikan nilai ini juga dikonversi ke float Python biasa
            rf = model.named_steps["clf"]
            importances = rf.feature_importances_
            numeric_features = df_input.select_dtypes(include=["int64", "float64"]).columns
            idx_sorted = np.argsort(importances[:len(numeric_features)])[::-1]
            top_features = numeric_features[idx_sorted[:2]]
            # Gunakan .item() untuk mengubah numpy ke python standar
            top_values = [df_input[feat].iloc[0].item() if hasattr(df_input[feat].iloc[0], 'item') else df_input[feat].iloc[0] for feat in top_features]

            # 5. Simpan ke MySQL
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                sql = """
                INSERT INTO rekam_medis (
                    no_rekam_medis, nama_pasien, gender, age, height, weight, 
                    family_history_with_overweight, FAVC, FCVC, NCP, CAEC, SMOKE, 
                    CH2O, SCC, FAF, TUE, CALC, MTRANS, status, proba
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                # Semua variabel di sini harus tipe Python (str, int, float), bukan NumPy
                val = (
                    str(no_rm), str(nama_pasien),
                    str(data["Gender"]), float(data["Age"]), float(data["Height"]), float(data["Weight"]),
                    int(data["family_history_with_overweight"]), int(data["FAVC"]), 
                    float(data["FCVC"]), float(data["NCP"]), str(data["CAEC"]), int(data["SMOKE"]), 
                    float(data["CH2O"]), int(data["SCC"]), float(data["FAF"]), float(data["TUE"]), 
                    str(data["CALC"]), str(data["MTRANS"]),
                    str(status), float(proba)
                )
                cursor.execute(sql, val)
                conn.commit()
                cursor.close()
                conn.close()

            return render_template(
                "result.html",
                nama=nama_pasien,
                status=status,
                proba=round(proba, 3),
                top_features=zip(top_features, top_values),
                advice=advice_list,
            )

        except Exception as e:
            # Cetak error ke terminal agar kita bisa melacak detailnya
            print(f"DEBUG ERROR: {e}")
            return f"Terjadi kesalahan: {e}", 500

    return render_template("form.html")

# 5. ROUTE LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/history")
def history():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) # Menggunakan dictionary agar mudah dibaca di HTML
    
    # Mengambil semua data dari yang terbaru
    cursor.execute("SELECT * FROM rekam_medis ORDER BY created_at DESC")
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template("history.html", data=rows)

@app.route("/delete_history/<int:id>")
def delete_history(id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Perintah hapus berdasarkan ID
    cursor.execute("DELETE FROM rekam_medis WHERE id = %s", (id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    # Setelah hapus, kembali ke halaman riwayat
    return redirect(url_for("history"))
