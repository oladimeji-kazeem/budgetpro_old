import csv
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from setup.models import DateDetail # Import the model from the local app

# Define the name of the column in your CSV that contains the date
date_column_name = 'Date' 

class Command(BaseCommand):
    help = 'Imports date dimension data from a specified CSV file into the DateDetail model.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file to import')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        
        try:
            # --- FIX: Changed encoding from 'utf-8' to 'latin-1' to bypass 0x81 error ---
            with open(csv_file_path, mode='r', encoding='latin-1') as file:
                reader = csv.DictReader(file)
                
                if date_column_name not in reader.fieldnames:
                    # Fallback check: If the header is missing, check the file name.
                    if 'date_table_2015_2030.xlsx - Sheet1.csv' in csv_file_path:
                        self.stdout.write(self.style.WARNING("The date file name suggests a possible file type issue or missing 'Date' header."))
                    raise CommandError(f"CSV file must contain a column named '{date_column_name}'. Please verify the header in your CSV.")

                imported_count = 0
                skipped_count = 0
                
                for row in reader:
                    date_str = row.get(date_column_name)
                    
                    if not date_str:
                        self.stdout.write(self.style.WARNING(f"Skipping row with missing date value: {row}"))
                        skipped_count += 1
                        continue

                    try:
                        # Attempt to parse date in common formats
                        try:
                            # Standard YYYY-MM-DD
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                        except ValueError:
                            # Try common European/US formats if standard fails (e.g., DD/MM/YYYY or MM/DD/YYYY)
                            try:
                                date_obj = datetime.strptime(date_str, '%m/%d/%Y').date()
                            except ValueError:
                                try:
                                    date_obj = datetime.strptime(date_str, '%d/%m/%Y').date()
                                except ValueError:
                                    raise ValueError("Date string is not in a recognizable format.")

                    except ValueError as ve:
                         self.stdout.write(self.style.ERROR(f"Skipping row. Could not parse date '{date_str}'. Date format is invalid. Error: {ve}"))
                         skipped_count += 1
                         continue

                    # Prevent duplicate creation
                    if DateDetail.objects.filter(date=date_obj).exists():
                        self.stdout.write(self.style.NOTICE(f"Date {date_obj} already exists, skipping."))
                        skipped_count += 1
                        continue
                    
                    try:
                        # Create object. The custom save() method calculates dimensional fields.
                        DateDetail.objects.create(date=date_obj)
                        imported_count += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error importing date {date_obj}: {e}"))
                        skipped_count += 1
                        
                self.stdout.write(self.style.SUCCESS(f'Successfully imported {imported_count} new date records.'))
                if skipped_count > 0:
                    self.stdout.write(self.style.WARNING(f'Skipped {skipped_count} records (duplicates or errors).'))

        except FileNotFoundError:
            raise CommandError(f'File not found at path: {csv_file_path}')
        except Exception as e:
            # Re-raise error if not a file-related or UnicodeDecodeError (which is fixed)
            self.stdout.write(self.style.ERROR(f'An unexpected error occurred during import: {e}'))