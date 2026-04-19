"""Tests for anonymizer.anonymize_rows and PII_TRANSFORMERS.

All tests follow the AAA pattern. Imports will fail until TASK-05 creates
the module — that is the intended red state.
"""

from __future__ import annotations

import hashlib

import pytest

from app.services.anonymizer import PII_TRANSFORMERS, anonymize_rows

_COLUMNS_CONSUMIDOR = ["id_pedido", "nome_consumidor", "valor_total"]
_COLUMNS_VENDEDOR = ["id_pedido", "nome_vendedor", "valor_total"]


# ---------------------------------------------------------------------------
# Disabled mode — no-op
# ---------------------------------------------------------------------------


def test_no_masking_when_disabled() -> None:
    rows = [["1", "João Silva", 99.9]]

    result = anonymize_rows(_COLUMNS_CONSUMIDOR, rows, enabled=False)

    assert result == rows


# ---------------------------------------------------------------------------
# Hash determinism
# ---------------------------------------------------------------------------


def test_hash_nome_consumidor_deterministic() -> None:
    rows = [["1", "Maria Souza", 50.0]]

    first = anonymize_rows(_COLUMNS_CONSUMIDOR, rows, enabled=True)
    second = anonymize_rows(_COLUMNS_CONSUMIDOR, rows, enabled=True)

    assert first == second
    assert first[0][1].startswith("Consumidor_")


def test_hash_nome_vendedor_deterministic() -> None:
    rows = [["1", "Carlos Lima", 200.0]]

    first = anonymize_rows(_COLUMNS_VENDEDOR, rows, enabled=True)
    second = anonymize_rows(_COLUMNS_VENDEDOR, rows, enabled=True)

    assert first == second
    assert first[0][1].startswith("Vendedor_")


def test_different_names_produce_different_hashes() -> None:
    row_a = [["1", "Ana Costa", 10.0]]
    row_b = [["1", "Bruno Reis", 10.0]]

    result_a = anonymize_rows(_COLUMNS_CONSUMIDOR, row_a, enabled=True)
    result_b = anonymize_rows(_COLUMNS_CONSUMIDOR, row_b, enabled=True)

    assert result_a[0][1] != result_b[0][1]


def test_hash_uses_sha1_truncated_to_6_chars() -> None:
    name = "Teste Unitario"
    expected_suffix = hashlib.sha1(name.encode("utf-8")).hexdigest()[:6]
    rows = [["1", name, 0.0]]

    result = anonymize_rows(_COLUMNS_CONSUMIDOR, rows, enabled=True)

    assert result[0][1] == f"Consumidor_{expected_suffix}"


# ---------------------------------------------------------------------------
# CEP masking
# ---------------------------------------------------------------------------


def test_mask_prefixo_cep() -> None:
    columns = ["prefixo_cep"]
    rows = [["01310"]]

    result = anonymize_rows(columns, rows, enabled=True)

    assert result[0][0] == "01***"


# ---------------------------------------------------------------------------
# Comment redaction
# ---------------------------------------------------------------------------


def test_redact_comentario_truncates_and_masks_numbers() -> None:
    # Number 12345 starts at char 9, well inside the 40-char window
    long_comment = "Pedido 12345 aprovado. " + "x" * 40
    columns = ["comentario"]
    rows = [[long_comment]]

    result = anonymize_rows(columns, rows, enabled=True)

    masked = result[0][0]
    assert len(masked) <= 41  # 40 chars + ellipsis character
    assert "***" in masked
    assert "12345" not in masked


# ---------------------------------------------------------------------------
# Non-PII passthrough
# ---------------------------------------------------------------------------


def test_preserves_non_pii_columns() -> None:
    columns = ["id_pedido", "valor_total", "status"]
    rows = [["42", 199.9, "entregue"]]

    result = anonymize_rows(columns, rows, enabled=True)

    assert result[0] == ["42", 199.9, "entregue"]


# ---------------------------------------------------------------------------
# Null-safety
# ---------------------------------------------------------------------------


def test_handles_null_values() -> None:
    columns = ["nome_consumidor", "prefixo_cep", "comentario"]
    rows = [[None, None, None]]

    result = anonymize_rows(columns, rows, enabled=True)

    assert result[0] == [None, None, None]


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_pii_transformers_contains_expected_keys() -> None:
    expected = {
        "nome_consumidor",
        "nome_vendedor",
        "autor_resposta",
        "prefixo_cep",
        "comentario",
        "titulo_comentario",
    }

    assert expected == set(PII_TRANSFORMERS.keys())


def test_handles_empty_rows_list() -> None:
    result = anonymize_rows(_COLUMNS_CONSUMIDOR, [], enabled=True)

    assert result == []


def test_column_order_independence() -> None:
    columns_ab = ["nome_consumidor", "prefixo_cep"]
    columns_ba = ["prefixo_cep", "nome_consumidor"]
    row_ab = [["João Silva", "01310"]]
    row_ba = [["01310", "João Silva"]]

    result_ab = anonymize_rows(columns_ab, row_ab, enabled=True)
    result_ba = anonymize_rows(columns_ba, row_ba, enabled=True)

    assert result_ab[0][0] == result_ba[0][1]  # nome masked consistently
    assert result_ab[0][1] == result_ba[0][0]  # cep masked consistently


def test_mismatched_row_length_raises() -> None:
    columns = ["nome_consumidor", "valor_total"]
    rows_too_short = [["João Silva"]]  # missing second column

    with pytest.raises(ValueError):
        anonymize_rows(columns, rows_too_short, enabled=True)
