from PySide6.QtWidgets import QLineEdit

def optional_text(field: QLineEdit) -> str | None:
    value = field.text().strip()
    return value if value else None

def format_model_for_display(data) -> str:
    """Converts any Pydantic model returned from the API into a
    human-readable string for message boxes.
    Works for any model - Business, Site, or anything added later.
    """
    lines = []
    for field, value in data.model_dump().items():
        label = field.replace("_", " ").title()  # turns "is_supplier" into "Is Supplier"
        if value is None:
            display = "Not provided"
        elif isinstance(value, bool):
            display = "Yes" if value else "No"
        else:
            display = str(value)
        lines.append(f"{label}: {display}")
    return "\n".join(lines)
