# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 13:12:28 2020

@author: Info
"""


import pandas as pd
from datetime import timedelta
from datetime import datetime
import numpy as np

def formataCpfCns(colunaCpf, colunaCns):
    for index, value in colunaCpf.items():
        if(len(str(colunaCns[index])) != 15):
            colunaCns[index] = None
        if(pd.isnull(value)):
            colunaCpf[index] = None
            continue
        value = value.strip()
        value = value.replace(".", "")
        value = value.replace("-", "")
        while len(value) < 11:
            value = "0" + value
        colunaCpf[index] = str(value)
        # if(len(colunaCpf[index]) < 14):
        #     colunaCpf[index] = value[:3] + '.' + value[3:6] + "." + value[6:9] + "-" + value[9:]
    return colunaCpf, colunaCns

def acharId(Cpf, Cns, Nome, Dn, tabela):
    #print("TESTE - DN param " + str(Dn) + "\nPrimeira data da tabela: " + str(tabela['Data Nasc.'][0]))
    if(type(Cpf) is float):
        print("ACHEI UM CPF FLOAT: " + str(Cpf) + "\nNome: " + str(Nome))
    if(Cpf is not None):
        filtro1 = tabela['CPF'] == Cpf.strip()
    else:
        filtro1 = False
        
    if(Cns is not None):
        filtro2 = tabela['CNS'] == Cns.strip()
    else:
        filtro2 = False
        
    if(Nome is not None and Dn is not None):
        filtro3 = tabela['Paciente'] == Nome.strip()
        filtro4 = tabela['Data Nasc.'] == Dn
    else:
        filtro3 = False
        filtro4 = False
    teste = tabela.where(filtro1 | filtro2 | (filtro3 & filtro4)).dropna(how='all')
    return teste

def mascaraDataEsus(tabelaEsus):
    if tabelaEsus.empty:
        return tabelaEsus
    colunasData = ['Data da NotificaCAo', 'Data de Nascimento', 'Data do inIcio dos sintomas']
    for i in colunasData:
        tabelaEsus[i] = tabelaEsus[i].dt.strftime('%d/%m/%Y')
    return tabelaEsus

def limpaUtf8(tabela): #Função que limpa os caracteres bugados do UTF-8 do arquivo de exportação do eSUS
    tabela.replace(to_replace={"Ã§": "C", "Ã‡": "C", "Ãµ": "O", "Ã³": "O", "Ã´": "O", "Ã\”": "O", "Ã­": "I", "Ãº": "U", "Ãš": "U", "ÃŠ": "E", "Ãª": "E", "Ã©": "E", "Ã‰": "E", "ÃG": "IG", "Ãƒ": "A", "Ã£": "A", "Ã¡": "A", "Ã¢": "A"}, inplace=True, regex=True)
    tabela.replace(to_replace={"Ã": "A"}, inplace=True, regex=True)
    tabela.rename(columns={"Data da NotificaÃ§Ã£o": "Data da NotificaCAo", "Resultado (PCR/RÃ¡pidos)": "Resultado (PCR/RApidos)", "MunicÃ­pio de ResidÃªncia": "MunicIpio de ResidEncia", "Data do inÃ­cio dos sintomas": "Data do inIcio dos sintomas"}, inplace=True)
    return tabela

def limpaAcentos(tabela): #Função que limpa os caracteres especiais da tabela do Assessor
    tabela.replace(to_replace={"Á": "A", "á": "A", "Â": "A", "â": "A", "Ã": "A", "ã": "A",
                               "É": "E", "é": "E", "Ê": "E", "ê": "E",
                               "Í": "I", "í": "I", "Î": "I", "î": "I",
                               "Ó": "O", "ó": "O", "Ô": "O", "ô": "O", "Õ": "O", "õ": "O",
                               "Ú": "U", "ú": "U", "Û": "U", "û": "U",
                               "Ç": "C", "ç": "C"}, inplace=True, regex=True)
    tabela.rename(columns={"Cód. Paciente": "COd. Paciente", "Data da Notificação": "Data da NotificaCAo", "Situação": "SituaCAo"}, inplace=True)    
    return tabela

paramDiasAtras = 15 #Parâmetro que define quantos dias atrás ele considera na planilha de suspeitos e monitoramento (ex: notificações de até X dias atrás serão analisadas, antes disso serão ignoradas)
paramDiasNegativo = 5 #Parâmetro que define quantos dias atrás uma notificacao de negativo deve ser considerada "a mesma" notificacao. Acima desse parâmetro deve ser considerada uma nova notificacao
paramColunaNomeEsus = 59 ##Parâmetro que define qual é o index da coluna que possui o nome completo do paciente no eSUS (parâmetro necessário pois o itertuples não permite indexacao por nome de coluna com espaço)
paramColunaDataNascEsus = 52 ##Parâmetro que define qual é o index da coluna que possui a data de nascimento do paciente no eSUS (parâmetro necessário pois o itertuples não permite indexacao por nome de coluna com espaço)
paramColunaDataNotifEsus = 13 #Parâmetro que define qual é o index da coluna que possui a data de notificacao do eSUS (parâmetro necessário pois o itertuples não permite indexacao por nome de coluna com espaço)
paramColunaDataNotifAssessor = 11 #Parâmetro igual ao paramColunaDataNotifEsus porém para o Assessor
paramDataAtual = datetime.today() #Parâmetro que define qual é a data atual para o script fazer a comparacao dos dias para trás (padrão: datetime.today() = data atual do sistema)

print("Data de hoje: " + datetime.today().strftime("%d/%m/%Y"))
print("Data de 15 dias atrás: " + (datetime.today() - timedelta(days=15)).strftime("%d/%m/%Y"))

tabelaTotalEsus = pd.read_excel("exportacao.xlsx", dtype={'CPF': np.unicode_, 'CNS': np.unicode_}).sort_values(by="Data da NotificaÃ§Ã£o", ignore_index=True) #Lista total das notificações do eSus
tabelaTotalEsus['CPF'], tabelaTotalEsus['CNS'] = formataCpfCns(tabelaTotalEsus['CPF'], tabelaTotalEsus['CNS'])
tabelaTotalEsus['Nome Completo'] = tabelaTotalEsus['Nome Completo'].str.upper()
tabelaTotalEsus = limpaUtf8(tabelaTotalEsus)

tabelaTotalStc = tabelaTotalEsus
#tabelaTotalPio = tabelaTotalEsus

filtroPosStc1 = tabelaTotalStc["Resultado Totais"] == "Reagente"
filtroPosStc2 = tabelaTotalStc["Resultado IgA"] == "Reagente"
filtroPosStc3 = tabelaTotalStc["Resultado (PCR/RApidos)"] == "Positivo"
filtroPosStc4 = tabelaTotalStc["Resultado IgM"] == "Reagente"
filtroPosStc5 = tabelaTotalStc["Resultado IgG"] == "Reagente"

tabelaPositivosStc = tabelaTotalStc.where(filtroPosStc1 | filtroPosStc2 | filtroPosStc3 | filtroPosStc4 | filtroPosStc5).dropna(how='all').drop_duplicates("CPF", ignore_index=True, keep='last')
#tabelaPositivosPio = tabelaTotalPio.where(tabelaTotalPio["Resultado do Teste"] == "Positivo").dropna(how='all').drop_duplicates("CPF", ignore_index=True, keep='last')

# tabelaNegativosStc = tabelaTotalStc.where(tabelaTotalStc["Resultado do Teste"] == "Negativo").dropna(how='all')
#tabelaNegativosPio = tabelaTotalPio.where(tabelaTotalPio["Resultado do Teste"] == "Negativo").dropna(how='all')

# tabelaSemResultadoStc = tabelaTotalStc.where(pd.isnull(tabelaTotalStc["Resultado do Teste"])).dropna(how='all')
#tabelaSemResultadoPio = tabelaTotalPio.where(pd.isnull(tabelaTotalPio["Resultado do Teste"])).dropna(how='all')

# tabelaSuspeitosStc = tabelaSemResultadoStc.where(tabelaTotalStc["Estado do Teste"] == "Coletado").dropna(how='all').drop_duplicates("CPF", ignore_index=True, keep='last')
# tabelaSuspeitosStc = tabelaSuspeitosStc.where(tabelaSuspeitosStc["Data da NotificaÃ§Ã£o"] >= (paramDataAtual - timedelta(days=paramDiasAtras))).dropna(how='all')
#tabelaSuspeitosPio = tabelaSemResultadoPio.where(tabelaTotalPio["Estado do Teste"] == "Coletado").dropna(how='all').drop_duplicates("CPF", ignore_index=True, keep='last')
#tabelaSuspeitosPio = tabelaSuspeitosPio.where(tabelaSuspeitosPio["Data da NotificaÃ§Ã£o"] >= (paramDataAtual - timedelta(days=paramDiasAtras))).dropna(how='all')

# tabelaMonitoramentoStc = tabelaSemResultadoStc.where(tabelaSemResultadoStc["Estado do Teste"] != "Coletado").dropna(how='all').drop_duplicates("CPF", ignore_index=True, keep='last')
# tabelaMonitoramentoStc = tabelaMonitoramentoStc.where(tabelaMonitoramentoStc["Data da NotificaÃ§Ã£o"] >= paramDataAtual - timedelta(days=paramDiasAtras)).dropna(how='all')
#tabelaMonitoramentoPio = tabelaSemResultadoPio.where(tabelaSemResultadoPio["Estado do Teste"] != "Coletado").dropna(how='all').drop_duplicates("CPF", ignore_index=True, keep='last')
#tabelaMonitoramentoPio = tabelaMonitoramentoPio.where(tabelaMonitoramentoPio["Data da NotificaÃ§Ã£o"] >= paramDataAtual - timedelta(days=paramDiasAtras)).dropna(how='all')

tabelaTotalAssessor = pd.read_excel("lista total assessor.xls", dtype={'CPF': np.unicode_, 'CNS': np.unicode_}).sort_values(by=["Cód. Paciente", "Data da Notificação"])
tabelaTotalAssessor['CPF'], tabelaTotalAssessor['CNS'] = formataCpfCns(tabelaTotalAssessor['CPF'], tabelaTotalAssessor['CNS'])
tabelaTotalAssessor = limpaAcentos(tabelaTotalAssessor)

# tabelaMonitoramentoStcFalso = []
# tabelaSuspeitosStcFalso = []
tabelaPositivosStcFalso = []
# tabelaNegativosStcFalso = []

#tabelaMonitoramentoPioFalso = []
#tabelaSuspeitosPioFalso = []
#tabelaPositivosPioFalso = []
#tabelaNegativosPioFalso = []

# for row in tabelaMonitoramentoStc.itertuples():
#     notifAssessor = acharId(row.CPF, row.CNS, row[paramColunaNomeEsus], row[paramColunaDataNascEsus], tabelaTotalAssessor)
#     if "CONFIRMADO" in notifAssessor["Situacao"].values:
#         #print("Achei um confirmado!")
#         tabelaMonitoramentoStcFalso.append({"Nome": row[paramColunaNomeEsus], "CPF": row.CPF, "Motivo": "CONFIRMADO"})
#         tabelaMonitoramentoStc.drop(row.Index, inplace=True)
#         continue
#     if "SUSPEITA" in notifAssessor["Situacao"].values:
#         tabelaMonitoramentoStcFalso.append({"Nome": row[paramColunaNomeEsus], "CPF": row.CPF, "Motivo": "SUSPEITO EM ABERTO"})
#         tabelaMonitoramentoStc.drop(row.Index, inplace=True)
#         continue
#     if "NEGATIVO" in notifAssessor["Situacao"].values:
#         negativosAssessor = notifAssessor.where(notifAssessor["Situacao"] == "NEGATIVO").dropna(how='all')
#         for rowNegativo in negativosAssessor.itertuples():
#             flagIsWrong = False #Flag que indica se a notificacao do eSUS é incorreta por já haver negativo no período indicado pelo parâmetro. Flag usada para sair corretamente dos laços.
#             dataNotifAssessor = rowNegativo[paramColunaDataNotifAssessor]
#             dataNotifEsus = row[paramColunaDataNotifEsus]
#             if dataNotifAssessor >= dataNotifEsus - timedelta(days=paramDiasNegativo):
#                 flagIsWrong = True
#                 break
#         if flagIsWrong:
#             tabelaMonitoramentoStcFalso.append({"Nome": row[paramColunaNomeEsus], "CPF": row.CPF, "Motivo": "NEGATIVO DENTRO DO PERIODO"})
#             tabelaMonitoramentoStc.drop(row.Index, inplace=True)
#             continue      

# for row in tabelaSuspeitosStc.itertuples():
#     notifAssessor = acharId(row.CPF, row.CNS, row[paramColunaNomeEsus], row[paramColunaDataNascEsus], tabelaTotalAssessor)
#     # print("TESTE: " + str(row[paramColunaDataNascEsus]))
#     if "CONFIRMADO" in notifAssessor["Situacao"].values:
#         #print("Achei um confirmado!")
#         tabelaSuspeitosStcFalso.append({"Nome": row[paramColunaNomeEsus], "CPF": row.CPF, "Motivo": "CONFIRMADO"})
#         tabelaSuspeitosStc.drop(row.Index, inplace=True)
#         continue
#     if "SUSPEITA" in notifAssessor["Situacao"].values:
#         tabelaSuspeitosStcFalso.append({"Nome": row[paramColunaNomeEsus], "CPF": row.CPF, "Motivo": "SUSPEITO EM ABERTO"})
#         tabelaSuspeitosStc.drop(row.Index, inplace=True)
#         continue
#     if "NEGATIVO" in notifAssessor["Situacao"].values:
#         negativosAssessor = notifAssessor.where(notifAssessor["Situacao"] == "NEGATIVO").dropna(how='all')
#         for rowNegativo in negativosAssessor.itertuples():
#             flagIsWrong = False #Flag que indica se a notificacao do eSUS é incorreta por já haver negativo no período indicado pelo parâmetro. Flag usada para sair corretamente dos laços.
#             dataNotifAssessor = rowNegativo[paramColunaDataNotifAssessor]
#             dataNotifEsus = row[paramColunaDataNotifEsus]
#             if dataNotifAssessor >= dataNotifEsus - timedelta(days=paramDiasNegativo):
#                 flagIsWrong = True
#                 break
#         if flagIsWrong:
#             tabelaSuspeitosStcFalso.append({"Nome": row[paramColunaNomeEsus], "CPF": row.CPF, "Motivo": "NEGATIVO DENTRO DO PERIODO"})
#             tabelaSuspeitosStc.drop(row.Index, inplace=True)
#             continue
        
for row in tabelaPositivosStc.itertuples():
    notifAssessor = acharId(row.CPF, row.CNS, row[paramColunaNomeEsus], row[paramColunaDataNascEsus], tabelaTotalAssessor)
    # print("TESTE: " + str(row[paramColunaDataNascEsus]))
    if "CONFIRMADO" in notifAssessor["SituaCAo"].values:
        #print("Achei um confirmado!")
        tabelaPositivosStcFalso.append({"Nome": row[paramColunaNomeEsus], "CPF": row.CPF, "Motivo": "CONFIRMADO"})
        tabelaPositivosStc.drop(row.Index, inplace=True)
        continue
    
# for row in tabelaNegativosStc.itertuples():
#     notifAssessor = acharId(row.CPF, row.CNS, row[paramColunaNomeEsus], row[paramColunaDataNascEsus], tabelaTotalAssessor)
#     # print("TESTE: " + str(row[paramColunaDataNascEsus]))
#     if "CONFIRMADO" in notifAssessor["Situacao"].values:
#         #print("Achei um confirmado!")
#         tabelaNegativosStcFalso.append({"Nome": row[paramColunaNomeEsus], "CPF": row.CPF, "Motivo": "CONFIRMADO"})
#         tabelaNegativosStc.drop(row.Index, inplace=True)
#         continue    
#     if "NEGATIVO" in notifAssessor["Situacao"].values:
#         negativosAssessor = notifAssessor.where(notifAssessor["Situacao"] == "NEGATIVO").dropna(how='all')
#         for rowNegativo in negativosAssessor.itertuples():
#             flagIsWrong = False #Flag que indica se a notificacao do eSUS é incorreta por já haver negativo no período indicado pelo parâmetro. Flag usada para sair corretamente dos laços.
#             dataNotifAssessor = rowNegativo[paramColunaDataNotifAssessor]
#             dataNotifEsus = row[paramColunaDataNotifEsus]
#             if dataNotifAssessor >= dataNotifEsus - timedelta(days=paramDiasNegativo):
#                 flagIsWrong = True
#                 break
#         if flagIsWrong:
#             tabelaNegativosStcFalso.append({"Nome": row[paramColunaNomeEsus], "CPF": row.CPF, "Motivo": "NEGATIVO DENTRO DO PERIODO"})
#             tabelaNegativosStc.drop(row.Index, inplace=True)
#             continue
        
# for row in tabelaMonitoramentoPio.itertuples():
#     notifAssessor = acharId(row.CPF, row.CNS, row[paramColunaNomeEsus], row[paramColunaDataNascEsus], tabelaTotalAssessor)
#     if "CONFIRMADO" in notifAssessor["Situacao"].values:
#         #print("Achei um confirmado!")
#         tabelaMonitoramentoPioFalso.append({"Nome": row[paramColunaNomeEsus], "CPF": row.CPF, "Motivo": "CONFIRMADO"})
#         tabelaMonitoramentoPio.drop(row.Index, inplace=True)
#         continue
#     if "SUSPEITA" in notifAssessor["Situacao"].values:
#         tabelaMonitoramentoPioFalso.append({"Nome": row[paramColunaNomeEsus], "CPF": row.CPF, "Motivo": "SUSPEITO EM ABERTO"})
#         tabelaMonitoramentoPio.drop(row.Index, inplace=True)
#         continue
#     if "NEGATIVO" in notifAssessor["Situacao"].values:
#         negativosAssessor = notifAssessor.where(notifAssessor["Situacao"] == "NEGATIVO").dropna(how='all')
#         for rowNegativo in negativosAssessor.itertuples():
#             flagIsWrong = False #Flag que indica se a notificacao do eSUS é incorreta por já haver negativo no período indicado pelo parâmetro. Flag usada para sair corretamente dos laços.
#             dataNotifAssessor = rowNegativo[paramColunaDataNotifAssessor]
#             dataNotifEsus = row[paramColunaDataNotifEsus]
#             if dataNotifAssessor >= dataNotifEsus - timedelta(days=paramDiasNegativo):
#                 flagIsWrong = True
#                 break
#         if flagIsWrong:
#             tabelaMonitoramentoPioFalso.append({"Nome": row[paramColunaNomeEsus], "CPF": row.CPF, "Motivo": "NEGATIVO DENTRO DO PERIODO"})
#             tabelaMonitoramentoPio.drop(row.Index, inplace=True)
#             continue      

# for row in tabelaSuspeitosPio.itertuples():
#     notifAssessor = acharId(row.CPF, row.CNS, row[paramColunaNomeEsus], row[paramColunaDataNascEsus], tabelaTotalAssessor)
#     # print("TESTE: " + str(row[paramColunaDataNascEsus]))
#     if "CONFIRMADO" in notifAssessor["Situacao"].values:
#         #print("Achei um confirmado!")
#         tabelaSuspeitosPioFalso.append({"Nome": row[paramColunaNomeEsus], "CPF": row.CPF, "Motivo": "CONFIRMADO"})
#         tabelaSuspeitosPio.drop(row.Index, inplace=True)
#         continue
#     if "SUSPEITA" in notifAssessor["Situacao"].values:
#         tabelaSuspeitosPioFalso.append({"Nome": row[paramColunaNomeEsus], "CPF": row.CPF, "Motivo": "SUSPEITO EM ABERTO"})
#         tabelaSuspeitosPio.drop(row.Index, inplace=True)
#         continue
#     if "NEGATIVO" in notifAssessor["Situacao"].values:
#         negativosAssessor = notifAssessor.where(notifAssessor["Situacao"] == "NEGATIVO").dropna(how='all')
#         for rowNegativo in negativosAssessor.itertuples():
#             flagIsWrong = False #Flag que indica se a notificacao do eSUS é incorreta por já haver negativo no período indicado pelo parâmetro. Flag usada para sair corretamente dos laços.
#             dataNotifAssessor = rowNegativo[paramColunaDataNotifAssessor]
#             dataNotifEsus = row[paramColunaDataNotifEsus]
#             if dataNotifAssessor >= dataNotifEsus - timedelta(days=paramDiasNegativo):
#                 flagIsWrong = True
#                 break
#         if flagIsWrong:
#             tabelaSuspeitosPioFalso.append({"Nome": row[paramColunaNomeEsus], "CPF": row.CPF, "Motivo": "NEGATIVO DENTRO DO PERIODO"})
#             tabelaSuspeitosPio.drop(row.Index, inplace=True)
#             continue
        
# for row in tabelaPositivosPio.itertuples():
#     notifAssessor = acharId(row.CPF, row.CNS, row[paramColunaNomeEsus], row[paramColunaDataNascEsus], tabelaTotalAssessor)
#     # print("TESTE: " + str(row[paramColunaDataNascEsus]))
#     if "CONFIRMADO" in notifAssessor["Situacao"].values:
#         #print("Achei um confirmado!")
#         tabelaPositivosPioFalso.append({"Nome": row[paramColunaNomeEsus], "CPF": row.CPF, "Motivo": "CONFIRMADO"})
#         tabelaPositivosPio.drop(row.Index, inplace=True)
#         continue
    
# for row in tabelaNegativosPio.itertuples():
#     notifAssessor = acharId(row.CPF, row.CNS, row[paramColunaNomeEsus], row[paramColunaDataNascEsus], tabelaTotalAssessor)
#     # print("TESTE: " + str(row[paramColunaDataNascEsus]))
#     if "CONFIRMADO" in notifAssessor["Situacao"].values:
#         #print("Achei um confirmado!")
#         tabelaNegativosPioFalso.append({"Nome": row[paramColunaNomeEsus], "CPF": row.CPF, "Motivo": "CONFIRMADO"})
#         tabelaNegativosPio.drop(row.Index, inplace=True)
#         continue    
#     if "NEGATIVO" in notifAssessor["Situacao"].values:
#         negativosAssessor = notifAssessor.where(notifAssessor["Situacao"] == "NEGATIVO").dropna(how='all')
#         for rowNegativo in negativosAssessor.itertuples():
#             flagIsWrong = False #Flag que indica se a notificacao do eSUS é incorreta por já haver negativo no período indicado pelo parâmetro. Flag usada para sair corretamente dos laços.
#             dataNotifAssessor = rowNegativo[paramColunaDataNotifAssessor]
#             dataNotifEsus = row[paramColunaDataNotifEsus]
#             if dataNotifAssessor >= dataNotifEsus - timedelta(days=paramDiasNegativo):
#                 flagIsWrong = True
#                 break
#         if flagIsWrong:
#             tabelaNegativosPioFalso.append({"Nome": row[paramColunaNomeEsus], "CPF": row.CPF, "Motivo": "NEGATIVO DENTRO DO PERIODO"})
#             tabelaNegativosPio.drop(row.Index, inplace=True)
#             continue

with pd.ExcelWriter('Externas ' + paramDataAtual.strftime("%d.%m") + '.xlsx') as writerStcCorreto:
    # tabelaMonitoramentoStc = mascaraDataEsus(tabelaMonitoramentoStc)    
    # tabelaMonitoramentoStc.to_excel(writerStcCorreto, "Monitoramento")    
    
    # tabelaSuspeitosStc = mascaraDataEsus(tabelaSuspeitosStc)    
    # tabelaSuspeitosStc.to_excel(writerStcCorreto, "Suspeitos")    
    
    tabelaPositivosStc = mascaraDataEsus(tabelaPositivosStc)    
    tabelaPositivosStc.to_excel(writerStcCorreto, "Positivos")    
    
    # tabelaNegativosStc = mascaraDataEsus(tabelaNegativosStc)
    # tabelaNegativosStc.to_excel(writerStcCorreto, "Negativos")
    
# with pd.ExcelWriter('PIO XII ' + paramDataAtual.strftime("%d.%m") + '.xlsx') as writerPioCorreto:
#     tabelaMonitoramentoPio = mascaraDataEsus(tabelaMonitoramentoPio)    
#     tabelaMonitoramentoPio.to_excel(writerPioCorreto, "Monitoramento")    
    
#     tabelaSuspeitosPio = mascaraDataEsus(tabelaSuspeitosPio)    
#     tabelaSuspeitosPio.to_excel(writerPioCorreto, "Suspeitos")    
    
#     tabelaPositivosPio = mascaraDataEsus(tabelaPositivosPio)    
#     tabelaPositivosPio.to_excel(writerPioCorreto, "Positivos")    
    
#     tabelaNegativosPio = mascaraDataEsus(tabelaNegativosPio)    
#     tabelaNegativosPio.to_excel(writerPioCorreto, "Negativos")  
    
with pd.ExcelWriter('INCORRETO EXTERNAS ' + paramDataAtual.strftime("%d.%m") + '.xlsx') as writerIncorreto:
    # tabelaMonitoramentoStcFalso = pd.DataFrame(tabelaMonitoramentoStcFalso)
    # tabelaMonitoramentoStcFalso.to_excel(writerIncorreto, "Monitoramento StaCasa")
    # tabelaMonitoramentoPioFalso = pd.DataFrame(tabelaMonitoramentoPioFalso)
    # tabelaMonitoramentoPioFalso.to_excel(writerIncorreto, "Monitoramento Pio XII")
    
    # tabelaSuspeitosStcFalso = pd.DataFrame(tabelaSuspeitosStcFalso)
    # tabelaSuspeitosStcFalso.to_excel(writerIncorreto, "Suspeitos StaCasa")
    # tabelaSuspeitosPioFalso = pd.DataFrame(tabelaSuspeitosPioFalso)
    # tabelaSuspeitosPioFalso.to_excel(writerIncorreto, "Suspeitos Pio XII")
    
    tabelaPositivosStcFalso = pd.DataFrame(tabelaPositivosStcFalso)
    tabelaPositivosStcFalso.to_excel(writerIncorreto, "Positivos StaCasa")
    # tabelaPositivosPioFalso = pd.DataFrame(tabelaPositivosPioFalso)
    # tabelaPositivosPioFalso.to_excel(writerIncorreto, "Positivos Pio XII")
    
    # tabelaNegativosStcFalso = pd.DataFrame(tabelaNegativosStcFalso)
    # tabelaNegativosStcFalso.to_excel(writerIncorreto, "Negativos StaCasa")
    # tabelaNegativosPioFalso = pd.DataFrame(tabelaNegativosPioFalso)
    # tabelaNegativosPioFalso.to_excel(writerIncorreto, "Negativos Pio XII")