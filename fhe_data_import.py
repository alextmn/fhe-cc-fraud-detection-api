import csv
import datetime

from fhe_dao import CcFeatureRow

def import_csv_to_mongo(csv_file_path: str = "some_cc_transactions.csv", 
                        principal_id: str= "alice-1", username="alice"):
    with open(csv_file_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Build the list of floats for the v_vector field
            v_values = []
            for i in range(1, 29):  # 1..28 inclusive
                # Convert each V column string to float
                v_str = row[f"V{i}"]
                v_values.append(float(v_str))

            # Parse amount
            amount_value = float(row["Amount"]) if row["Amount"] else 0.0

            # Parse Time if it’s in a known format, e.g. "YYYY-MM-DD HH:MM:SS"
            # Adjust strptime format to match your actual CSV data
            # If "Time" is not parseable, handle accordingly
            tx_date_value = None
            if row["Time"]:
                try:
                    tx_date_value = datetime.datetime.strptime(row["Time"], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    # If your CSV date format is different, adjust above or handle error
                    pass

            # Create and save the document
            cc_feature_row = CcFeatureRow(
                key_id=None,
                tx_date=tx_date_value,         # parsed datetime
                principal_id=principal_id,      
                username=username,          
                v_vector=v_values,
                encrypted=None,                # not in CSV
                decrypted=None,                # not in CSV
                actual=row["Class"],           # from CSV
                inference=None,                # not in CSV
                amount=amount_value,
                status="unprocessed",          
                encrypted_ts=None,             # not in CSV
                calculated_ts=None             # not in CSV
            )
            cc_feature_row.save()
            # Optionally print/log
            print(f"Inserted row: id={cc_feature_row.key_id}")