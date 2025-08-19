# To run these tests, use `poetry run pytest` in your terminal.

# Import the function from your main script file.
from clarifica.core import process_line_spans

# --- TEST SUITE FOR SUPERSCRIPT DETECTION ---

def test_deve_detectar_superscript_simples_corretamente():
    """Tests the basic case: Word followed by a smaller number."""
    spans = [
        {"text": "Jung", "size": 12.0},
        {"text": "2", "size": 8.0}
    ]
    assert process_line_spans(spans) == "Jung<sup>2</sup>"

def test_deve_detectar_superscript_multidigito():
    """Ensures that multi-digit numbers are also converted."""
    spans = [
        {"text": "Freud", "size": 12.0},
        {"text": "12", "size": 8.0},
    ]
    assert process_line_spans(spans) == "Freud<sup>12</sup>"

def test_deve_detectar_superscript_apos_pontuacao():
    """Checks if detection works after punctuation."""
    spans = [
        {"text": "francos;", "size": 12.0},
        {"text": "6", "size": 9.0},
    ]
    assert process_line_spans(spans) == "francos;<sup>6</sup>"

def test_espaco_em_span_separado_nao_quebra_superscript():
    """
    Tests if the logic correctly ignores a space span between the
    word and the citation number.
    """
    spans = [
        {"text": "Jung", "size": 12.0},
        {"text": " ", "size": 12.0},  # Space as a separate span
        {"text": "2", "size": 8.0},
    ]
    # The refactored logic now correctly skips the space span.
    assert process_line_spans(spans) == "Jung <sup>2</sup>"

def test_numero_apos_numero_nao_deve_virar_superscript():
    """
    Tests the false positive case: a smaller number following another number
    should not be treated as a citation.
    """
    spans = [
        {"text": "p. ", "size": 12.0},
        {"text": "12", "size": 12.0},
        {"text": "3", "size": 9.0},  # Smaller, but follows a number
    ]
    # The new logic should prevent this conversion.
    assert process_line_spans(spans) == "p. 123"

def test_diferenca_de_tamanho_insuficiente_nao_vira_superscript():
    """
    This test currently fails because we haven't implemented a threshold.
    It serves as a placeholder for a future enhancement.
    """
    spans = [
        {"text": "Autor", "size": 12.0},
        {"text": "2", "size": 11.0},  # Only slightly smaller
    ]
    # Current behavior:
    assert process_line_spans(spans) == "Autor<sup>2</sup>"
    # Desired future behavior with a threshold (e.g., 15% smaller):
    # assert process_line_spans(spans) == "Autor2"

def test_nao_deve_confundir_data_com_superscript():
    """Ensures that regular numbers with the same font size are not affected."""
    spans = [
        {"text": "ano ", "size": 12.0},
        {"text": "2024", "size": 12.0}
    ]
    assert process_line_spans(spans) == "ano 2024"
