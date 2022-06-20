## @package entradaSD
#  Documentation for this module.
#
#  More details.
import socket
import sys
import json
import time
from _thread import *

## The socket 1
# Cria o socket que ira se escutar as conexões de outros hosts
entrada = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
entrada.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

## The argc, argv
#  Verifica se os parametros de entrada de execução estão corretos
#  More details.
if len(sys.argv) != 3:
	print ("Uso correto: script endereço porta")
	exit()

## Binda o ponto de entrada e escuta por novas conexões. (Maximo de 100)
endereco_ip = str(sys.argv[1])
porta = int(sys.argv[2])
entrada.bind((endereco_ip, porta))
entrada.listen(100)

## Inicialiaza como vazia a lista de conexões
conexoes = []

## Function host
#  @param(host)
#  Esta função executa a partir de uma thread que escuta por novos hosts que entraram no SD
def host(conexao):
	enderecoHost = json.loads(conexao.recv(2048).decode("utf8"))
	print(f"{enderecoHost[0]}:{enderecoHost[1]} se conectou")

	conexaoInfo = {
		"id": len(conexoes),
		"endereco": enderecoHost[0],
		"porta": enderecoHost[1]
	}
	conexoes.append(conexaoInfo)

	while True:
		time.sleep(1)
		try:
			conexao.send(bytes(json.dumps(conexoes, indent=4, ensure_ascii=True) + "\n\n", "utf8"))
		except:
			remover(conexaoInfo)
			print(f"{conexaoInfo['endereco']}:{conexaoInfo['porta']} se desconectou")
			break

## Function remover
#  @param(host)
#  Remove um nó da lista de hosts do SD
def remover(conexao):
	if conexao in conexoes:
		conexoes.remove(conexao)

## Ciclo que escuta por novos hosts que se conectarão
while True:
	conexao, endereco = entrada.accept()

	start_new_thread(host, (conexao, ))

conexao.close()
entrada.close()
