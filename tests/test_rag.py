from src.rag.generator import ResponseGenerator
from src.rag.retriever import Retriever, ResultadoBusca


class FakeVectorStore:
    def __init__(self, resultados):
        self.resultados = resultados

    def buscar(self, pergunta, top_k=5, filtro_categoria=None):
        return self.resultados


class FakeLLMProvider:
    def __init__(self, resposta="Resposta baseada no contexto."):
        self.resposta = resposta
        self.prompts = []

    def gerar_resposta(self, prompt):
        self.prompts.append(prompt)
        return self.resposta


def _resultado(documento="doc-017", distancia=0.3):
    return {
        "texto": "O limite diário padrão para Pix é de R$ 5.000 durante o dia.",
        "metadata": {
            "documento_id": documento,
            "titulo": "Regras de Limites, Pix e Liquidação",
            "categoria": "transacoes",
            "chunk_indice": 0,
        },
        "distancia": distancia,
    }


def test_retriever_aceita_contexto_dentro_do_limiar():
    store = FakeVectorStore([_resultado(distancia=0.3)])
    retriever = Retriever(store, limiar_distancia=0.8)

    resultado = retriever.buscar("Qual é o limite do Pix?")

    assert resultado.tem_contexto_suficiente is True
    assert len(resultado.trechos) == 1


def test_retriever_rejeita_contexto_fora_do_limiar():
    store = FakeVectorStore([_resultado(distancia=0.9)])
    retriever = Retriever(store, limiar_distancia=0.8)

    resultado = retriever.buscar("Qual é a capital da França?")

    assert resultado.tem_contexto_suficiente is False
    assert resultado.trechos == []


def test_generator_usa_contexto_e_retorna_fontes():
    llm = FakeLLMProvider()
    generator = ResponseGenerator(llm)

    busca = ResultadoBusca(
        trechos=[_resultado()],
        tem_contexto_suficiente=True,
    )

    resposta = generator.gerar(
        "Qual é o limite do Pix?",
        busca,
    )

    assert resposta.teve_fallback is False
    assert "Regras de Limites, Pix e Liquidação" in resposta.fontes[0]["documento"]
    assert resposta.fontes[0]["categoria"] == "transacoes"
    assert len(llm.prompts) == 1
    assert "R$ 5.000" in llm.prompts[0]


def test_generator_faz_fallback_sem_contexto():
    llm = FakeLLMProvider()
    generator = ResponseGenerator(llm)

    busca = ResultadoBusca(
        trechos=[],
        tem_contexto_suficiente=False,
    )

    resposta = generator.gerar(
        "Qual é a capital da França?",
        busca,
    )

    assert resposta.teve_fallback is True
    assert resposta.fontes == []
    assert len(llm.prompts) == 0
