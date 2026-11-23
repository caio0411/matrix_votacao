"""Testes das regras da enquete. Rodar com: python -m unittest -v"""

import unittest

from enquete import processar_comando

ANA = "@ana:localhost"
BETO = "@beto:localhost"


class TestEnquete(unittest.TestCase):
    def criar_enquete(self):
        estado, _ = processar_comando("!enquete Melhor linguagem? | Python | Go", ANA, None)
        return estado

    def test_criar_enquete(self):
        estado = self.criar_enquete()
        self.assertEqual(estado["pergunta"], "Melhor linguagem?")
        self.assertEqual(estado["opcoes"], ["Python", "Go"])
        self.assertTrue(estado["aberta"])
        self.assertEqual(estado["criador"], ANA)

    def test_enquete_precisa_de_duas_opcoes(self):
        estado, resposta = processar_comando("!enquete So uma? | Sim", ANA, None)
        self.assertIsNone(estado)
        self.assertIn("Formato", resposta)

    def test_nao_cria_duas_enquetes_abertas(self):
        estado = self.criar_enquete()
        novo, resposta = processar_comando("!enquete Outra? | A | B", BETO, estado)
        self.assertIsNone(novo)
        self.assertIn("Já existe", resposta)

    def test_votar_e_contar(self):
        estado = self.criar_enquete()
        estado, _ = processar_comando("!votar 1", ANA, estado)
        estado, _ = processar_comando("!votar 2", BETO, estado)
        self.assertEqual(estado["votos"], {ANA: 1, BETO: 2})

    def test_votar_de_novo_troca_o_voto(self):
        estado = self.criar_enquete()
        estado, _ = processar_comando("!votar 1", ANA, estado)
        estado, resposta = processar_comando("!votar 2", ANA, estado)
        self.assertEqual(estado["votos"], {ANA: 2})
        self.assertIn("trocou", resposta)

    def test_opcao_invalida(self):
        estado = self.criar_enquete()
        novo, resposta = processar_comando("!votar 9", ANA, estado)
        self.assertIsNone(novo)
        self.assertIn("inválida", resposta)

    def test_votar_sem_enquete(self):
        novo, resposta = processar_comando("!votar 1", ANA, None)
        self.assertIsNone(novo)
        self.assertIn("Não há enquete", resposta)

    def test_so_criador_encerra(self):
        estado = self.criar_enquete()
        novo, resposta = processar_comando("!encerrar", BETO, estado)
        self.assertIsNone(novo)
        novo, resposta = processar_comando("!encerrar", ANA, estado)
        self.assertFalse(novo["aberta"])
        self.assertIn("Resultado final", resposta)

    def test_nao_vota_em_enquete_encerrada(self):
        estado = self.criar_enquete()
        estado, _ = processar_comando("!encerrar", ANA, estado)
        novo, resposta = processar_comando("!votar 1", BETO, estado)
        self.assertIsNone(novo)

    def test_resultado_mostra_porcentagem(self):
        estado = self.criar_enquete()
        estado, _ = processar_comando("!votar 1", ANA, estado)
        _, resposta = processar_comando("!resultado", BETO, estado)
        self.assertIn("1) Python: 1 voto(s) (100%)", resposta)

    def test_texto_comum_e_ignorado(self):
        self.assertEqual(processar_comando("bom dia!", ANA, None), (None, None))
        self.assertEqual(processar_comando("!comando_que_nao_existe", ANA, None), (None, None))


if __name__ == "__main__":
    unittest.main()
