from pathlib import Path

from src.ingestion.loaders import carregar_csv, carregar_json, carregar_markdown


def test_carregar_markdown(tmp_path: Path):
    arquivo = tmp_path / "doc.md"
    arquivo.write_text("# Título\n\nConteúdo.", encoding="utf-8")
    assert "Título" in carregar_markdown(arquivo)


def test_carregar_csv(tmp_path: Path):
    arquivo = tmp_path / "dados.csv"
    arquivo.write_text("nome,valor\nTarifa TED,8.90\n", encoding="utf-8")
    resultado = carregar_csv(arquivo)
    assert "nome: Tarifa TED" in resultado
    assert "valor: 8.90" in resultado


def test_carregar_json(tmp_path: Path):
    arquivo = tmp_path / "dados.json"
    arquivo.write_text('{"categoria": "tarifas", "itens": [{"nome": "TED"}]}', encoding="utf-8")
    resultado = carregar_json(arquivo)
    assert "categoria: tarifas" in resultado
    assert "itens.0.nome: TED" in resultado
