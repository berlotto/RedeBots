############################### Sobre #################################
# Programa para realizar o processamento da linguagem natural.
#
#
# Referência: *inserir referencias para basearmo-nos*
#
import os
import json

def interpretador(palavras):
    '''
    Procura no dicionario as perguntas e devolve a resposta.
    '''
    def lista_perguntas():
        endereco = os.getcwd() + "/perguntas_respostas.txt" #os.getcwd() retora o diretorio corrente de trabalho.
        arq = open(endereco)
        for line in arq:
            dicionario = json.loads(line)
        return dicionario
    dicionario = lista_perguntas()

    try:
        resposta = dicionario[palavras]
    except KeyError:
        resposta = "não entendi"

    return resposta
