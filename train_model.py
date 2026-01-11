# train_model.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import pickle

def main():
    # === 1. Load data ===
    csv_path = "obesity_level.csv"
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: {csv_path} not found.")
        return

    # === 2. Preprocessing ===

    # 2.1 Drop kolom id
    if "id" in df.columns:
        df = df.drop(columns=["id"])

    # 2.2 Nama kolom target asli
    target_col = "0be1dad"

    # 2.3 Filter hanya Normal & Overweight (tanpa Obesity dan Insufficient)
    allowed_classes = [
        "Normal_Weight",
        "0rmal_Weight",
        "Overweight_Level_I",
        "Overweight_Level_II",
    ]
    df = df[df[target_col].isin(allowed_classes)].copy()

    # 2.4 Mapping label -> 0 (Normal) dan 1 (Resiko_Obesitas = Overweight)
    normal_classes = ["Normal_Weight", "0rmal_Weight"]
    risk_classes = ["Overweight_Level_I", "Overweight_Level_II"]

    def map_label(label: str) -> int:
        if label in normal_classes:
            return 0
        elif label in risk_classes:
            return 1
        else:
            return None

    df["target_binary"] = df[target_col].apply(map_label)

    # 2.5 Buang baris label None, ubah ke int
    df = df[df["target_binary"].notnull()].copy()
    df["target_binary"] = df["target_binary"].astype(int)

    # 2.6 Buang duplikat
    df = df.drop_duplicates()

    # 2.7 Buang missing values
    df = df.dropna()

    # === 3. Siapkan X dan y ===
    X = df.drop(columns=["target_binary", target_col])
    y = df["target_binary"]

    numeric_features = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_features = X.select_dtypes(include=["object"]).columns.tolist()

    categorical_transformer = OneHotEncoder(handle_unknown="ignore")

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )

    # === 4. Model Random Forest ===
    rf = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    )

    model = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("clf", rf),
        ]
    )

    # === 5. train_test_split 80:20 ===
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # === 6. Train dan evaluasi ===
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    with open("prediksi.pkl", "wb") as f:
        pickle.dump(model, f)
    print("Model saved to prediksi.pkl")

if __name__ == "__main__":
    main()
