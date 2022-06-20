## @package hostsSD
#  Documentation for this module.
#
#  More details.
import socket
import json
from tabnanny import check
import time
import sys
import random
import string
from _thread import *

## The argc, argv
#  Verifica se os parametros de entrada de execução estão corretos
#  More details.
if len(sys.argv) != 5:
	print ("Uso correto: script endereço_entrada porta_entrada endereço porta")
	exit()

## The socket 1
# Cria o socket que ira se escutar as conexões de outros hosts
endereco_entrada = str(sys.argv[1])
porta_entrada = int(sys.argv[2])
endereco = str(sys.argv[3])
porta = int(sys.argv[4])
esteHost = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
esteHost.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
entrada = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
entrada.connect((endereco_entrada, porta_entrada))

## Inicializa 1
#  Inicializa as variáveis
conexoes = []
conexoes_entrada = []
idConectado = None
idMensagem = ""
conexaoHost = None

## Function PING
#  @param host que será conectado
#  Esta função, dado uma novo host for criado, é testado com todos os hosts
#  do Sistema (SD) e é retornado o host de menor atraso
def pingConexoes(conexoes):
	global conexaoHost
	menorTempo = 0
	global host

	for _conexao in conexoes:
		if _conexao['endereco'] == endereco and _conexao['porta'] == porta:
			continue

		host = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print(f"Testando {_conexao['endereco']}:{_conexao['porta']}...")
		time.sleep(1)
		inicio = time.time()
		host.connect((_conexao["endereco"], _conexao["porta"]))
		fim = time.time()
		host.send(bytes(json.dumps([endereco, porta, 0], indent=4, ensure_ascii=True), "utf8"))
		host.close()
		print(f"{(fim - inicio)*1000} ms")

		if menorTempo != 0:
			if fim - inicio < menorTempo:
				menorTempo = fim - inicio
				conexaoHost = _conexao
		else:
			menorTempo = fim - inicio
			conexaoHost = _conexao

## Function manterConexaoEntrada
#  Esta função executa a partir deu uma thread, a qual mantem os hosts 
#  do ponto de entrada atualizados em todos os hosts do SD
def manterConexaoEntrada():
	global conexoes_entrada
	global conexaoHost
	conectado = False
	procurandoConexao = False

	while True:
		## Mantem a conecção, tolerando a desconexão de um no host
		if not conectado and not procurandoConexao:
			start_new_thread(procurarConexao, ())
			procurandoConexao = True
		try:
			__conexoes_entrada = entrada.recv(2048).decode("utf8")
			__conexoes_entrada = __conexoes_entrada.split('\n\n')
			for _conexoes_entrada in __conexoes_entrada:
				if _conexoes_entrada == '':
					continue
				conexoes_entrada = json.loads(_conexoes_entrada)
				conectado = False
				for conexao_entrada in conexoes_entrada:
					if conexao_entrada['endereco'] == conexaoHost['endereco'] and conexao_entrada['porta'] == conexaoHost['porta']:
						conectado = True
						procurandoConexao = False
						break
		except:
			continue

## Function receberConexoes
#  @param host
#  Remove o host da lista de hosts conectados
def receberConexoes(esteEndereco, estaPorta):
	esteHost.bind((esteEndereco, estaPorta))
	esteHost.listen(100)

	while True:
		conexao, endereco = esteHost.accept()

		while True:
			mensagem = conexao.recv(2048).decode("utf8")
			if mensagem != "":
				break
		enderecoHost = json.loads(mensagem)

		for conexao_entrada in conexoes_entrada:
			if conexao_entrada['endereco'] == enderecoHost[0] and conexao_entrada['porta'] == enderecoHost[1]:
				break

		if enderecoHost[2] == 1:
			print(f"O host de id {conexao_entrada['id']} se conectou aqui")
			start_new_thread(repassarMensagem, (conexao,))
			conexoes.append(conexao)

## Function remover
#  @param host
#  Remove o host da lista de hosts conectados
def remover(conexao):
	if conexao in conexoes:
		conexoes.remove(conexao)

## Function repassarMensagem
#  @param host
#  Esta função executa a partir de uma thread e receber as mensagem dos 
#  hosts conectados, ela verifica se a mensagem recebida ja foi repassada 
#  por ela mesma para enviar para outro host
def repassarMensagem(conexao):
	global conexoes
	global idMensagem

	while True:
		try:
			_mensagem = conexao.recv(2048).decode("utf8")
		except:
			remover(conexao)
			break

		_mensagens = _mensagem.split('\n\n')
		for _mensagem in _mensagens:
			if _mensagem == '':
				continue
			mensagem = json.loads(_mensagem)
## verificação de que se a mensagem ja foi repasada
			if mensagem['id'] != idMensagem:
				idMensagem = mensagem['id']
				if mensagem["endereco"] != f"{endereco}:{porta}":
					print(f"{mensagem['id']}: {mensagem['conteudo']}")
				for _conexao in conexoes:
					try:
						_conexao.send(bytes(json.dumps(mensagem, indent=4, ensure_ascii=True) + "\n\n", "utf8"))
					except:
						_conexao.close()

						remover(_conexao)

## Function procurarConexao
#  Função que procura por uma conexão ao inicia o script de novo host
#  @return {retorn o host que sera conectado ao novo nó}
def procurarConexao():
	global conexaoHost
	global idConectado
	global host
	while True:
		pingConexoes(conexoes_entrada)
		if conexaoHost != None:
			idConectado = conexaoHost['id']
			break

	time.sleep(1)
	host = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	host.connect((conexaoHost['endereco'], conexaoHost['porta']))
	host.send(bytes(json.dumps([endereco, porta, 1], indent=4, ensure_ascii=True), "utf8"))
	print(f"Este host se conectou com o host de id {idConectado}")
	conexoes.append(host)
	time.sleep(1)
	start_new_thread(repassarMensagem, (host,))

## Envia o endereço e porta para se salvo no ponto de entrada
entrada.send(bytes(json.dumps([endereco, porta], indent=4, ensure_ascii=True), "utf8"))

## Inicia novas threads
start_new_thread(manterConexaoEntrada, ())
start_new_thread(receberConexoes, (endereco, porta))

## Ciclo que envia novas mensagens para os hosts conectados com ele
while True:
	conteudo = sys.stdin.readline()

	idMensagem = ""
	for i in range(5):
		idMensagem += random.choice(string.ascii_letters)
## Cria o json de mensagem
	mensagem = {
		"id": idMensagem,
		"endereco": f"{endereco}:{porta}",
		"conteudo": conteudo.strip('\n')
	}

## Envia a mensagem para todos dos os conectados
	for _conexao in conexoes:
		try:
			_conexao.send(bytes(json.dumps(mensagem, indent=4, ensure_ascii=True) + "\n\n", "utf8"))
		except:
			_conexao.close()

			remover(_conexao)

	sys.stdout.write("<Você>")
	sys.stdout.write(mensagem["conteudo"] + '\n')
	sys.stdout.flush()


host.close()
entrada.close()
