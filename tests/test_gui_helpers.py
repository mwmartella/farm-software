# tests/test_gui_helpers.py
from GUI.helpers import optional_text, format_model_for_display
from unittest.mock import MagicMock
from schema.business import BusinessRead
from datetime import datetime
import uuid

def test_optional_text_returns_none_when_empty():
    # Simulate a blank QLineEdit without needing a real GUI
    mock_field = MagicMock()
    mock_field.text.return_value = ""
    assert optional_text(mock_field) is None

def test_optional_text_returns_stripped_value():
    # Whitespace should be stripped and value returned
    mock_field = MagicMock()
    mock_field.text.return_value = "  Test Farm  "
    assert optional_text(mock_field) == "Test Farm"

def test_format_model_displays_none_as_not_provided():
    # None values should display as "Not provided" not "None"
    business = BusinessRead(
        id=uuid.uuid4(),
        name="Test Farm",
        code="TF001",
        abn=None,
        phone=None,
        email=None,
        is_supplier=False,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    result = format_model_for_display(business)
    assert "Not provided" in result
    assert "None" not in result     # "None" should never be shown to the user

def test_format_model_displays_bool_as_yes_no():
    # Booleans should display as Yes/No not True/False
    business = BusinessRead(
        id=uuid.uuid4(),
        name="Test Farm",
        code="TF001",
        is_supplier=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    result = format_model_for_display(business)
    assert "Yes" in result
    assert "True" not in result     # "True" should never be shown to the user
