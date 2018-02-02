#
# Programa principal do bot para responder perguntas frequentes.
#
# O objetivo inicial é escrever um bot capaz de responder perguntas semelhantes às perguntas frequentes e indicar caso seja feita uma pergunta diferente.
#
# TODO:
#    * Implementar processador de linguagem natural para entender as perguntas realizadas ao bot.
#    * Fazer lista de perguntas e respostas frequentes.
#    * Decidir e implementar ação para o caso de realização de pergunta nova.
#
# Jan Luc Tavares, fevereiro de 2018.


import json
import requests
import time
import os
import urllib #biblioteca necessaria para a codificacao do texto em forma de url
from secretoken import tokensecret
from interpreta_pergunta import interpretador


TOKEN = tokensecret()
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

global tentativas
tentativas = 0  # variavel que conta o numero de erros de conexao que obtivemos


def get_url(url):
    '''
    Envia a url para o Telegram.
    '''
    try:
        response = requests.get(url)
        content = response.content.decode("utf8")
        global tentativas
        tentativas =0
    except:
    #except ConnectionError:

        if tentativas>24:
            raise Exception('Nao foi possivel obter os updates depois de dois minutos de Errors')
        else:
            time.sleep(5)
            global tentativas
            tentativas = tentativas + 1
            print("{} Conexões consecutivas mal sucedidas".format(tentativas))
            content = "{\"ok\":true,\"result\":[]}" #mente para o bot que nada aconteceu
    return content


def get_json_from_url(url):
    '''
    Carrega a resposta do servidor em JSON de forma mais legivel.
    '''
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    '''
    Recebe as novas mensagens.
    '''
    url = URL + "getUpdates?timeout=120"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def get_next_update_id(updates):
    '''
    Informa qual o proximo update para avisar o servidor que já lidamos com os updates anteriores.
    '''
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return (max(update_ids) + 1)


def get_last_chat_id_and_text(updates):
    '''
    Obtem o ultimo texto e "ID" recebido para lidar com isso.
    '''
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

def send_message(text, chat_id, reply_markup=None):
    '''
    Envia mensagem com o texto para certo chat.
    reply_markup pode conter o json necessario para enviar um teclado personalizado.
    '''
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)


def send_pic(chat_id, file):
    url=URL+ "sendPhoto"
    files = {'photo': open('{}/{}'.format(os.getcwd(),file), 'rb')}
    data = {'chat_id' : chat_id}
    requests.post(url, files=files, data=data)

def build_keyboard(items):
    '''
    Constroi JSON que informa o Telegram qual deve ser o teclado personalizado.
    '''
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)

############# Respostas as entradas do usuario ########################
#######################################################################

def boas_vindas(chat_id, entrada=None):
    text = "Oi!\nVocê está falando com o Bot da Rede Fora do Eixo\nReceba minhas sinceras boas-vindas!\n Confira os comandos em /ajuda"
    send_message(text, chat_id)

def ajuda(chat_id,entrada=None):
    text="\n/start - Boas-vindas\nEm breve poderei responder as perguntas de forma mais fluida. Por enquanto, confira a lista dizendo /perguntas\nAbraço :D"
    send_message(text, chat_id)

def perguntas(chat_id,entrada=None):
    text = "Ta aí a lista de perguntas"
    keyboard = build_keyboard(list(dicionario.keys()))
    send_message(text, chat_id, keyboard)
entradas = { "/start" : boas_vindas,
           "/ajuda": ajuda,
            "/perguntas": perguntas
        }

# Fim da definicao de respostas possiveis
#############################################################################
def lista_perguntas():
    endereco = os.getcwd() + "/perguntas_respostas.txt" #os.getcwd() retora o diretorio corrente de trabalho.
    arq = open(endereco)
    for line in arq:
        dicionario = json.loads(line)
    return dicionario
dicionario = lista_perguntas()



def handle_updates(updates):
    '''
    Lida com os updates de acordo com a entrada.
    '''
    for update in updates["result"]:
        if "edited_message" in update.keys():
            try:
                chat = update["edited_message"]["chat"]["id"]
                text = "Essa história de editar mensagens não funciona comigo... \nEu vou me confundir e você também. \nTenta mandar uma mensagem nova <3"
                send_message(text,chat,None)
            except:
                print("algo deu errado quando alguem editou uma mensagem")
        else:
            try:
                text = update["message"]["text"]
                palavras = text.split()
                chat = update["message"]["chat"]["id"]
#               items = db.get_items()
                entradas[palavras[0]](chat, text)
            except KeyError:
                text = interpretador(update["message"]["text"])
                chat = update["message"]["chat"]["id"]
                send_message(text,chat,None)


def main():
    next_update_id = None

    while True:
        updates = get_updates(next_update_id)
        if len(updates["result"]) > 0:
            next_update_id = get_next_update_id(updates)
            handle_updates(updates)
        time.sleep(0.5)

if __name__ == '__main__':
    main()
