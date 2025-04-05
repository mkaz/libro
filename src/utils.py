from datetime import datetime


def validate_and_convert_date(date_str, field_name):
    if not date_str:  # Handle empty dates
        return True, None

    formats = [
        "%m/%d/%y",  # 1/24/15
        "%m/%d/%Y",  # 1/24/2015
        "%Y-%m-%d",  # 2015-01-24
        "%Y",  # Just the year
        "%B %d, %Y",  # March 14, 2024
        "%d %B %Y",  # 14 March 2024
    ]

    for fmt in formats:
        try:
            date_obj = datetime.strptime(date_str, fmt)
            if fmt == "%m/%d/%y":
                if date_obj.year > datetime.now().year:
                    date_obj = date_obj.replace(year=date_obj.year - 100)

            if fmt == "%Y":
                return True, f"{date_obj.year}-01-01"

            return True, date_obj.strftime("%Y-%m-%d")
        except ValueError:
            continue

    print(f"Error: Invalid date format in {field_name}: {date_str}")
    return False, None


def get_valid_input(prompt, validator=None, allow_empty=False, multiline=False):
    if not multiline:
        while True:
            value = input(prompt).strip()
            if not value and not allow_empty:
                print("This field cannot be empty. Please try again.")
                continue
            if validator and value:
                is_valid, converted_value = validator(value)
                if is_valid:
                    return converted_value if converted_value is not None else value
            else:
                return value
    else:
        print(prompt + " (Enter two consecutive blank lines to finish)")
        lines = []
        last_line_empty = False
        while True:
            line = input()  # Don't strip here to preserve indentation
            if not line.strip():
                if last_line_empty:
                    if not lines and not allow_empty:
                        print("This field cannot be empty. Please try again.")
                        continue
                    break
                last_line_empty = True
            else:
                last_line_empty = False
            lines.append(line)
        # Remove the last empty line that was used as a terminator
        if lines and not lines[-1].strip():
            lines.pop()
        return "\n".join(lines)
