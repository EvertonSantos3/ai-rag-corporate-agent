import json

from src.observability import logger


def test_registrar_execucao_grava_jsonl(tmp_path, monkeypatch):
    log_path = tmp_path / "execucoes.jsonl"
    monkeypatch.setattr(logger, "LOG_PATH", log_path)

    logger.registrar_execucao(
        pergunta="Qual é o limite do Pix?",
        resposta_texto="O limite diário padrão é de R$ 5.000,00.",
        fontes=[
            {
                "documento": "Regras de Limites, Pix e Liquidação",
                "categoria": "transacoes",
            }
        ],
        teve_fallback=False,
    )

    assert log_path.exists()

    linha = log_path.read_text(encoding="utf-8").strip()
    registro = json.loads(linha)

    assert registro["pergunta"] == "Qual é o limite do Pix?"
    assert registro["resposta"] == "O limite diário padrão é de R$ 5.000,00."
    assert registro["teve_fallback"] is False
    assert registro["fontes"][0]["categoria"] == "transacoes"
    assert "timestamp" in registro
