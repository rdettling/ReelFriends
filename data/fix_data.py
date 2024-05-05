import csv
import json


def extract_names(dict_like_string):
    """Extracts and joins the names from a string that resembles a list of dictionaries."""
    if not dict_like_string or dict_like_string.strip() in ["null", "[]"]:
        return ""  # Return an empty string for null or empty values

    try:
        # Replace single quotes with double quotes to make it JSON-parsable
        corrected_string = dict_like_string.replace("'", '"')
        # Parse the corrected JSON string
        parsed_json = json.loads(corrected_string)
        # Extract the 'name' values
        names = [
            item.get("name", "") for item in parsed_json
        ]  # Handle missing 'name' key
        # Join the names with a comma
        return ", ".join(names)
    except (json.JSONDecodeError, ValueError) as e:
        # In case of JSON parsing error, print the error and return an empty string
        print(f"Error parsing JSON: {e}")
        return ""


def extract_collection_name(dict_like_string):
    """Extracts the 'name' value from a 'belongs_to_collection' string."""
    if dict_like_string in [None, "null", "", "[]"]:  # Check for null or empty values
        return ""
    try:
        corrected_string = dict_like_string.replace("'", '"')
        parsed_json = json.loads(corrected_string)
        return parsed_json["name"] if "name" in parsed_json else ""
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON for collection: {e}")
        return ""


def process_movies(input_file, output_file):
    original_row_count = 0
    modified_row_count = 0
    skipped_row_count = 0
    new_id = 1  # Initialize the new ID counter

    with open(input_file, mode="r", encoding="utf-8") as infile, open(
        output_file, mode="w", newline="", encoding="utf-8"
    ) as outfile:
        reader = csv.DictReader(infile)
        # Update fieldnames, replace 'belongs_to_collection' with 'collection', and add 'id' at the start
        fieldnames = ["id"] + [
            field if field != "belongs_to_collection" else "collection"
            for field in reader.fieldnames
            if field not in ["original_title", "id"]
        ]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:
            original_row_count += 1

            # Skip rows where 'release_date' is null or empty
            if not row["release_date"]:
                skipped_row_count += 1
                continue

            try:
                # Assign the new ID and increment it
                row["id"] = new_id
                new_id += 1

                # Modify the relevant fields
                row["genres"] = extract_names(row["genres"])
                row["production_companies"] = extract_names(row["production_companies"])
                row["production_countries"] = extract_names(row["production_countries"])
                row["spoken_languages"] = extract_names(row["spoken_languages"])
                row["collection"] = extract_collection_name(
                    row.get("belongs_to_collection", "")
                )

                # Prepare the row for writing, aligning with the new fieldnames
                modified_row = {
                    fieldname: row.get(fieldname, "") for fieldname in fieldnames
                }

                # Write the modified row
                writer.writerow(modified_row)
                modified_row_count += 1
            except Exception as e:
                # Print the error and skip this row
                print(f"Error processing row: {e}. Skipping row.")
                skipped_row_count += 1

    print(f"Original CSV Row Count: {original_row_count}")
    print(f"Modified CSV Row Count: {modified_row_count}")
    print(f"Rows Not Added: {skipped_row_count}")


input_filename = "movies_raw.csv"
output_filename = "movies_clean.csv"
process_movies(input_filename, output_filename)
