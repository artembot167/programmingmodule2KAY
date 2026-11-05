
import pytest
from conftest import load

M = load(3)


def test_one_section():
    site = {
        "sections": [
            {"id": "about", "title": "Про нас"}
        ]
    }
    result = M.build_sections(site)
    assert "<h2>Про нас</h2>" in result


def test_empty_sections():
    with pytest.raises(ValueError, match="Немає розділів"):
        M.build_sections({"sections": []})


def test_special_characters():
    site = {
        "sections": [
            {
                "id": "about",
                "title": "Кава & чай",
                "paragraphs": ["Смачно <дуже>"],
                "facts": ["100% & якість"]
            }
        ]
    }
    result = M.build_sections(site)
    assert "Кава &amp; чай" in result
    assert "&lt;дуже&gt;" in result
    assert "100% &amp; якість" in result
