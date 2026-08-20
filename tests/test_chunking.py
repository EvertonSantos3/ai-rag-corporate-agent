from src.ingestion.chunking import dividir_em_chunks, limpar_texto


def test_limpar_texto_remove_espacos_duplicados():
    assert limpar_texto("a   b\n\n\n\nc") == "a b\n\nc"


def test_dividir_em_chunks_respeita_tamanho_maximo():
    texto = "Parágrafo um.\n\n" + ("x" * 900) + "\n\nParágrafo três."
    chunks = dividir_em_chunks(texto, documento_id="doc-teste", tamanho_maximo=800, sobreposicao=50)
    assert len(chunks) >= 2
    for c in chunks:
        assert len(c.texto) <= 800 + 1  # tolerância mínima


def test_dividir_em_chunks_preserva_metadata():
    chunks = dividir_em_chunks("texto simples", documento_id="doc-1", metadata={"categoria": "atendimento"})
    assert chunks[0].documento_id == "doc-1"
    assert chunks[0].metadata["categoria"] == "atendimento"
