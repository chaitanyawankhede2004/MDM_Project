import csv
from app import app
from models import db, College

def init_database():
    with app.app_context():
        # Create all tables according to models
        db.create_all()
        print("Tables created successfully.")
        
        # Check if colleges exist already to prevent duplicates
        if College.query.count() == 0:
            print("Importing CollegeData.csv...")
            try:
                colleges = []
                with open("CollegeData.csv", "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        college = College(
                            institute_name=row["Name of institute"],
                            course=row["Cource"], # "Cource" is spelled with a 'c' in the CSV header
                            opening_rank=int(row["Opening Rank"]),
                            closing_rank=int(row["Closing Rank"])
                        )
                        colleges.append(college)
                
                db.session.bulk_save_objects(colleges)
                db.session.commit()
                print("Database populated successfully from CollegeData.csv.")
            except Exception as e:
                print(f"Error loading CSV: {e}")
                db.session.rollback()
        else:
            print("Database already contains college data. Skipping import.")

if __name__ == "__main__":
    init_database()
