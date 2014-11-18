from enum import Enum

# 
class StatusQuestao(Enum):
	nao_revisada = 0 # quando o usuario cadastra a Questao mas ela nem foi liberada nem bloqueada
	liberada = 1     # quando algum admin liberou a questao para que esta possa aparecer em partidas
	bloqueada = 2    # quando algum admin por algum motivo nao aceitou a questao enviada

# quando é feito o envio de uma resposta
class RetornoResposta(Enum):
	error = 0       # retorna um atributo MESSAGE contendo alguma mensagem gerada pelo servidor
	continua = 1    # retorna dados da partida e a proxima questao a ser respondida
	fim_partida = 2 # redireciona usuario para tela de resultado do jogo