
import mysql.connector

def init_mysql():
    try:
        # Connect to MySQL Server (assume root/no password as per user code)
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        cursor = conn.cursor()

        # Create Database
        cursor.execute("CREATE DATABASE IF NOT EXISTS cbl_obesitas")
        print("Database 'cbl_obesitas' checked/created.")

        # Connect to the specific database
        conn.database = "cbl_obesitas"

        # Create Table
        table_query = """
        CREATE TABLE IF NOT EXISTS rekam_medis (
            id INT AUTO_INCREMENT PRIMARY KEY,
            no_rekam_medis VARCHAR(50),
            nama_pasien VARCHAR(100),

            gender VARCHAR(10),
            age FLOAT,
            height FLOAT,
            weight FLOAT,
            family_history_with_overweight TINYINT,
            FAVC TINYINT,
            FCVC FLOAT,
            NCP FLOAT,
            CAEC VARCHAR(20),
            SMOKE TINYINT,
            CH2O FLOAT,
            SCC TINYINT,
            FAF FLOAT,
            TUE FLOAT,
            CALC VARCHAR(20),
            MTRANS VARCHAR(30),

            status VARCHAR(30),
            proba FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(table_query)
        print("Table 'rekam_medis' checked/created.")

        cursor.close()
        conn.close()
        print("MySQL initialization complete.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

if __name__ == "__main__":
    init_mysql()
