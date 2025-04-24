from tqdm import tqdm
from colorama import Fore, Style, init
from concurrent.futures import ProcessPoolExecutor
import os
import re
import time
import string

# Inicializa cores
init(autoreset=True)

# ======================== FUNÇÕES DE BUSCA PARA OPÇÃO 1 ========================
def buscar_no_arquivo(padrao_arquivo):
    """Busca um padrão em um arquivo e retorna as linhas encontradas."""
    padrao, arquivo = padrao_arquivo
    linhas_encontradas = set()
    with open(arquivo, 'r', encoding='utf-8', errors='ignore') as f:
        for linha in f:
            if re.search(padrao, linha, re.IGNORECASE):
                linhas_encontradas.add(linha.strip())
    return linhas_encontradas

def buscar_em_arquivos_paralelo(padrao, arquivos):
    """Busca em vários arquivos usando paralelismo."""
    resultados = set()
    total_arquivos = len(arquivos)

    with ProcessPoolExecutor() as executor:
        jobs = ((padrao, arquivo) for arquivo in arquivos)
        for i, resultado_parcial in enumerate(executor.map(buscar_no_arquivo, jobs), start=1):
            progresso = (i / total_arquivos) * 100
            print(f"{Fore.GREEN}[{i}/{total_arquivos}] {Fore.WHITE}Procurando em: ({Fore.YELLOW}{progresso:.2f}%{Fore.WHITE})")
            resultados.update(resultado_parcial)

    return resultados

def limpar_caracteres_invalidos(nome_arquivo):
    nome_arquivo = re.sub(r'[\\/*?:"<>|]', '_', nome_arquivo)
    nome_arquivo = re.sub(r'^[.]', '', nome_arquivo)
    return nome_arquivo

def formatar_tempo(segundos):
    """Formata o tempo no formato MM:SS."""
    minutos = int(segundos // 60)
    segundos_rest = int(segundos % 60)
    return f"{minutos:02d}:{segundos_rest:02d}"

def banner_principal():
    print(f"""{Fore.CYAN}
███████╗███████╗ █████╗ ██████╗  ██████╗██╗  ██╗    ████████╗ ██████╗  ██████╗ ██╗     ███████╗
██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝██║  ██║    ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
███████╗█████╗  ███████║██████╔╝██║     ███████║       ██║   ██║   ██║██║   ██║██║     ███████╗
╚════██║██╔══╝  ██╔══██║██╔══██╗██║     ██╔══██║       ██║   ██║   ██║██║   ██║██║     ╚════██║
███████║███████╗██║  ██║██║  ██║╚██████╗██║  ██║       ██║   ╚██████╔╝╚██████╔╝███████╗███████║
╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝       ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝
{Style.RESET_ALL}""")

def menu():
    banner_principal()
    print(f"""{Fore.YELLOW}
O que você deseja fazer?

{Fore.GREEN}1️⃣  {Style.RESET_ALL}🔍 Pesquisa em vários arquivos
{Fore.GREEN}2️⃣  {Style.RESET_ALL}📁 Pesquisa em arquivo específico
{Fore.GREEN}3️⃣  {Style.RESET_ALL}📑 Juntar todos arquivos txt em um único sem duplicatas
{Fore.GREEN}4️⃣  {Style.RESET_ALL}✂️ Dividir arquivos em partes menores

{Fore.MAGENTA}Digite o número da opção desejada:{Style.RESET_ALL} """, end="")

def limpar_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def consulta_varios_txt():
    print(f"\n{Fore.CYAN}🔍 CONSULTA VÁRIOS TXT\n")
    
    padrao = input(f"{Fore.YELLOW}Digite a palavra-chave para buscar: {Style.RESET_ALL}").strip()

    if not padrao:
        print(f"{Fore.RED}Você deve digitar uma palavra-chave válida.")
        return

    print(f"{Fore.CYAN}Buscando por '{padrao}' nos arquivos .txt na pasta atual...")

    inicio = time.time()  # Início da contagem de tempo
    
    # Busca um padrão em todos os arquivos .txt na pasta atual
    pasta = os.getcwd()
    arquivos_txt = [os.path.join(pasta, f) for f in os.listdir(pasta) if f.endswith('.txt')]
    resultados = buscar_em_arquivos_paralelo(padrao, arquivos_txt)
    
    fim = time.time()     # Fim da contagem de tempo
    duracao = fim - inicio

    print(f"\n⏱ Tempo total de busca: {Fore.GREEN}{formatar_tempo(duracao)}")

    if resultados:
        pasta_resultados = os.path.join(os.getcwd(), 'ENCONTRADO')
        os.makedirs(pasta_resultados, exist_ok=True)
        nome_arquivo = limpar_caracteres_invalidos(padrao)
        arquivo_resultado = os.path.join(pasta_resultados, f"{nome_arquivo}.txt")
        with open(arquivo_resultado, 'w', encoding='utf-8') as f:
            f.write("\n".join(resultados))

        print(f"\n{Fore.CYAN}Total de resultados únicos encontrados: {Fore.GREEN}{len(resultados)}")
        print(f"{Fore.CYAN}Resultados salvos em: {Fore.GREEN}{arquivo_resultado}")
    else:
        print(f"{Fore.RED}Nenhum resultado encontrado.")

def consulta_unico_txt():
    print(f"\n{Fore.CYAN}📁 PESQUISA EM ARQUIVO ESPECÍFICO\n")
    
    # Perguntar qual arquivo o usuário deseja pesquisar
    escolha_arquivo = input(f"{Fore.YELLOW}Deseja pesquisar no arquivo padrão 'linhas_unicas.txt' ou em outro arquivo?\n"
                          f"1 - {Fore.CYAN}linhas_unicas.txt{Fore.YELLOW} (padrão)\n"
                          f"2 - Outro arquivo específico\n"
                          f"Escolha (1/2): {Style.RESET_ALL}").strip()
    
    if escolha_arquivo == "2":
        arquivo = input(f"{Fore.YELLOW}Digite o nome do arquivo específico: {Style.RESET_ALL}").strip()
        if not os.path.exists(arquivo):
            print(f"{Fore.RED}⚠ Arquivo '{arquivo}' não encontrado.")
            return
    else:
        arquivo = 'linhas_unicas.txt'
        if not os.path.exists(arquivo):
            print(f"{Fore.RED}⚠ Arquivo padrão '{arquivo}' não encontrado.")
            return
    
    palavra = input(f"{Fore.YELLOW}Digite a palavra ou expressão: {Style.RESET_ALL}").strip()
    if not palavra:
        print(f"{Fore.RED}⚠ Palavra inválida.")
        return

    encontrados, resultados = 0, []
    inicio = time.time()

    try:
        with open(arquivo, 'r', encoding='utf-8', errors='ignore') as f:
            total = sum(1 for _ in f)
            f.seek(0)
            for linha in tqdm(f, total=total, desc=f"🔍 Buscando em '{arquivo}'", ncols=90, colour='green'):
                if re.search(palavra, linha, re.IGNORECASE):
                    resultados.append(linha.strip())
                    encontrados += 1
    except Exception as e:
        print(f"{Fore.RED}⚠ Erro ao ler o arquivo: {e}")
        return

    fim = time.time()
    duracao = fim - inicio
    
    print(f"\n✅ {encontrados} resultado(s) encontrados")
    print(f"⏱ Tempo total de busca: {Fore.GREEN}{formatar_tempo(duracao)}")

    if encontrados:
        pasta = 'unicosTXTENCONTRADO'
        os.makedirs(pasta, exist_ok=True)
        nome = ''.join(c for c in palavra if c in "-_.() %s%s" % (string.ascii_letters, string.digits))
        caminho = os.path.join(pasta, f"{nome}_{os.path.splitext(os.path.basename(arquivo))[0]}.txt")
        with open(caminho, 'w', encoding='utf-8') as f_out:
            f_out.write('\n'.join(resultados))
        print(f"📁 Resultado salvo em: {Fore.GREEN}{caminho}")
    else:
        print(f"{Fore.RED}Nenhum resultado encontrado.")

def juntar_txts():
    print(f"\n{Fore.CYAN}📑 JUNTA TODOS ARQUIVOS EM UM ÚNICO TXT\n")
    destino = 'linhas_unicas.txt'
    arquivos = [f for f in os.listdir() if f.endswith('.txt') and f != destino]

    deletar = input(f"{Fore.MAGENTA}Deseja deletar os arquivos originais? (s/n): {Style.RESET_ALL}").lower() == 's'
    linhas = set()
    
    inicio = time.time()

    if os.path.exists(destino):
        with open(destino, 'r', encoding='utf-8', errors='ignore') as f:
            for linha in f:
                linha = linha.strip()
                if linha:
                    linhas.add(linha)

    novas = 0
    with open(destino, 'a', encoding='utf-8') as out:
        for nome in arquivos:
            with open(nome, 'r', encoding='utf-8', errors='ignore') as f:
                for linha in tqdm(f, desc=f"📄 {nome}", colour='cyan', leave=False):
                    linha = linha.strip()
                    if linha and linha not in linhas:
                        out.write(linha + '\n')
                        linhas.add(linha)
                        novas += 1
            if deletar:
                os.remove(nome)
                print(f"{Fore.RED}🗑️ {nome} deletado.")
            else:
                print(f"{Fore.GREEN}✅ {nome} mantido.")

    fim = time.time()
    duracao = fim - inicio

    print(f"\n✅ Novas linhas adicionadas: {novas}")
    print(f"📂 Total no '{destino}': {len(linhas)}")
    print(f"⏱ Tempo total de processamento: {Fore.GREEN}{formatar_tempo(duracao)}")

def dividir_txt():
    print(f"\n{Fore.CYAN}✂️ DIVIDIR TAMANHO DO TXT\n")
    nome = input(f"{Fore.YELLOW}Digite o nome do arquivo: {Style.RESET_ALL}").strip()
    if not os.path.exists(nome):
        print(f"{Fore.RED}⚠ Arquivo não encontrado.")
        return
    try:
        tamanho = int(input(f"{Fore.YELLOW}Tamanho máximo de cada parte (MB): {Style.RESET_ALL}"))
    except:
        print(f"{Fore.RED}⚠ Tamanho inválido.")
        return
    excluir = input(f"{Fore.MAGENTA}Excluir arquivo original após divisão? (s/n): {Style.RESET_ALL}").lower() == 's'

    inicio = time.time()
    
    tamanho_bytes = tamanho * 1024 * 1024
    with open(nome, 'rb') as arq:
        parte = 1
        while True:
            conteudo = arq.read(tamanho_bytes)
            if not conteudo:
                break
            novo = f"{os.path.splitext(nome)[0]}_parte{parte}.txt"
            with open(novo, 'wb') as saida:
                saida.write(conteudo)
            print(f"{Fore.GREEN}💾 Criado: {novo}")
            parte += 1

    if excluir:
        os.remove(nome)
        print(f"{Fore.RED}🗑️ {nome} excluído.")
    
    fim = time.time()
    duracao = fim - inicio
    
    print(f"\n✅ Arquivo dividido em {parte-1} partes")
    print(f"⏱ Tempo total de processamento: {Fore.GREEN}{formatar_tempo(duracao)}")

def executar_opcao(escolha):
    limpar_terminal()
    
    if escolha == '1':
        consulta_varios_txt()
    elif escolha == '2':
        consulta_unico_txt()
    elif escolha == '3':
        juntar_txts()
    elif escolha == '4':
        dividir_txt()
    else:
        print(f"{Fore.RED}⚠ Opção inválida!")
        return False
    
    return True

if __name__ == "__main__":
    while True:
        limpar_terminal()
        menu()
        escolha = input().strip()
        
        if executar_opcao(escolha):
            while True:
                continuar = input(f"\n{Fore.CYAN}🔁 Deseja voltar ao menu? (s/n) ou continuar com a mesma operação (c ou Enter): {Style.RESET_ALL}").lower()
                
                if continuar == 's':
                    # Voltar ao menu principal
                    break
                elif continuar == 'c' or continuar == '':
                    # Continuar com a mesma operação
                    limpar_terminal()
                    executar_opcao(escolha)
                else:
                    # Encerrar o programa
                    print(f"{Fore.GREEN}👋 Encerrando...")
                    exit()
        else:
            # Se a opção for inválida, pede para pressionar Enter para continuar
            input(f"\n{Fore.YELLOW}Pressione Enter para continuar...{Style.RESET_ALL}")