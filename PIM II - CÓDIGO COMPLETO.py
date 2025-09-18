# By Gabriel Schmeisk
from collections import deque # Importa a classe deque (fila dupla), usada para criar filas de alunos, por exemplo.
import os # Importa o módulo os, que permite interagir com o sistema operacional (criar pastas, manipular arquivos, etc.).
import random # Importa o módulo random, que permite gerar valores aleatórios (números, escolhas, etc.).
import string # Importa o módulo string, que contém constantes e funções relacionadas a strings (como letras, dígitos, etc.).


# --------------------- DICIONÁRIOS E FILAS --------------------- #

alunos = {}   # RA -> {"nome":, "turma":}
notas = {}    # RA -> {materia: media}
fila_alunos = deque() # Cria uma fila (deque) para armazenar os alunos em ordem de chegada (pode ser usada para chamadas, atendimento, etc.).
ras_existentes = set() # Cria um conjunto (set) para guardar todos os RAs já cadastrados, evitando duplicatas.

# Pasta onde os arquivos serão salvos
PASTA_ARQUIVOS = "dados_escolares"
if not os.path.exists(PASTA_ARQUIVOS):
    os.makedirs(PASTA_ARQUIVOS)


# --------------------- FUNÇÃO PARA CARREGAR DADOS --------------------- #

# Função para carregar dados do arquivo "alunos.txt" para os dicionários e filas
def carregar_dados():
    arquivo_alunos = os.path.join(PASTA_ARQUIVOS, "alunos.txt")  # Define o caminho completo do arquivo
    try:
        with open(arquivo_alunos, "r", encoding="utf-8") as f:  # Abre o arquivo para leitura
            ra_atual = None  # Inicializa variável para armazenar o RA atual
            for linha in f:  # Lê cada linha do arquivo
                linha = linha.strip()  # Remove espaços em branco no início/fim da linha
                
                # Cadastro de aluno
                if linha.startswith("Aluno -"):  # Identifica linhas que representam um aluno
                    partes = linha.split("|")  # Divide a linha em partes usando "|" como separador
                    nome = partes[0].replace("Aluno -", "").strip()  # Extrai o nome do aluno
                    ra = partes[1].replace("RA:", "").strip().upper()  # Extrai o RA do aluno e converte para maiúsculas
                    turma = partes[2].replace("Turma:", "").strip()  # Extrai a turma do aluno

                    alunos[ra] = {"nome": nome, "turma": turma}  # Adiciona aluno ao dicionário 'alunos'
                    fila_alunos.append(ra)  # Adiciona RA à fila de alunos
                    ras_existentes.add(ra)  # Adiciona RA ao conjunto de RAs existentes
                    ra_atual = ra  # Guarda o RA atual para associar notas a ele
                    continue  # Passa para a próxima linha

                # Cadastro de notas
                if ":" in linha and ra_atual and not linha.startswith("Média geral"):  # Verifica se a linha contém notas
                    notas[ra_atual] = notas.setdefault(ra_atual, {})  # Garante que existe um dicionário de notas para o RA
                    for parte in linha.split("|"):  # Divide as notas da linha
                        if ":" in parte:  # Só processa partes que têm ":"
                            materia, media = parte.split(":", 1)  # Separa matéria e média
                            materia, media = materia.strip(), media.strip()  # Remove espaços
                            if materia.lower() != "média geral":  # Ignora a média geral
                                notas[ra_atual][materia] = float(media)  # Armazena a nota como float
    except FileNotFoundError:  # Caso o arquivo não exista, ignora
        pass

# --------------------- FUNÇÃO PARA SALVAR DADOS --------------------- #

def salvar_dados():
    arquivo_alunos = os.path.join(PASTA_ARQUIVOS, "alunos.txt")  # Define caminho do arquivo
    with open(arquivo_alunos, "w", encoding="utf-8") as f:  # Abre o arquivo para escrita (sobrescreve o existente)
        f.write("© Todos os direitos reservados TecMais LTDA - 2025\n")
        f.write("=" * 60 + "\n\n")  # Linha separadora
        # Ordena turmas pelo nome
        for turma in sorted({info["turma"] for info in alunos.values()}):  # Cria conjunto de turmas e ordena
            f.write(f"===== TURMA {turma} =====\n\n")  # Escreve cabeçalho da turma

            # Ordena alunos por nome dentro da turma
            alunos_turma = sorted(
                (ra for ra, info in alunos.items() if info["turma"] == turma),  # Lista de RAs da turma
                key=lambda ra: alunos[ra]["nome"]  # Ordena pelo nome do aluno
            )

            for ra in alunos_turma:  # Para cada aluno da turma
                info = alunos[ra]  # Pega informações do aluno
                f.write(f"Aluno - {info['nome']} | RA: {ra} | Turma: {info['turma']}\n")  # Escreve linha do aluno

                # Notas do aluno
                notas_aluno = notas.get(ra, {})  # Pega notas do aluno, ou vazio se não existir
                if notas_aluno:  # Se houver notas
                    for materia, media in notas_aluno.items():  # Para cada matéria
                        f.write(f"{materia}: {media:.2f} | ")  # Escreve nota formatada com 2 casas decimais

                    media_geral = sum(notas_aluno.values()) / len(notas_aluno)  # Calcula média geral
                    f.write(f"Média geral: {media_geral:.2f}\n")  # Escreve média geral
                f.write("-" * 60 + "\n")  # Linha separadora

    # ---------------- SEPARAR ARQUIVOS DE CADA MATÉRIA ---------------- #

    materias_validas = ["Matematica", "Portugues", "Historia", "Geografia"]
    for materia in materias_validas:
        nome_arquivo = materia.lower() + ".txt"  # Nome do arquivo da matéria
        caminho_completo = os.path.join(PASTA_ARQUIVOS, nome_arquivo)
        with open(caminho_completo, "w", encoding="utf-8") as f_mat:
            f_mat.write(f"---- Notas de {materia} ----\n")  # Cabeçalho da matéria
            for ra in fila_alunos:  # Para cada aluno na fila
                nota = notas.get(ra, {}).get(materia)  # Pega a nota da matéria
                if nota is not None:  # Se existe nota
                    info = alunos[ra]  # Pega info do aluno
                    f_mat.write(
                        f"Aluno - {info['nome']} | RA: {ra} | Turma: {info['turma']} | Nota: {nota:.2f}\n"
                        + "-" * 60 + "\n"
                    )

    print("\nDados salvos com sucesso na pasta 'dados_escolares'!\n")



# --------------- FUNÇÃO CONSULTAR ALUNOS CADASTRADOS --------------- #

def listar_alunos():
    if not alunos:
        print("\nNenhum aluno cadastrado ainda.\n")
        input("Pressione qualquer tecla para continuar.")
        limpar_console()
        return

    print("\n===== ALUNOS POR TURMA =====\n")
    turmas = sorted({info["turma"] for info in alunos.values()})
    for turma in turmas:
        print(f"--- Turma {turma} ---")
        ras_turma = [ra for ra, info in alunos.items() if info["turma"] == turma]
        ras_turma.sort(key=lambda ra: alunos[ra]["nome"])
        
        for ra in ras_turma:
            info = alunos[ra]
            print(f"Nome: {info['nome']} | RA: {ra}")
        print()

    print("=======================================\n")
    input("Pressione qualquer tecla para continuar.")
    limpar_console()
    Menu_Inicial()



# --------------------- FUNÇÃO REMOVER ALUNO --------------------- #

def remover_aluno():
    print("""
=========================================
       ❌ REMOVER ALUNO DO SISTEMA ❌
=========================================
""")
    ra = input("🆔 Digite o RA do aluno que deseja remover: ").strip().upper()
    if ra not in alunos:
        print("\nAluno não encontrado!\n")
        input("Pressione qualquer tecla para continuar...")
        limpar_console()
        return


    confirmar = input(f"Tem certeza que deseja remover {alunos[ra]['nome']} do sistema? (Sim/Não): ").strip().upper()
    if confirmar == "sim":
        senha_correta = "aluno123"
        senha = input("Digite a senha para confirmar a exclusão do aluno: ").strip()
        if senha == senha_correta:
            alunos.pop(ra)
            notas.pop(ra, None)
            if ra in fila_alunos:
                fila_alunos.remove(ra)
            if ra in ras_existentes:
                ras_existentes.remove(ra)
            salvar_dados()
            print("\nAluno removido com sucesso!")
        else:
            print("Senha incorreta! Operação cancelada.")
            input("Pressione qualquer tecla para continuar.")

# --------------------- FUNÇÃO LIMPAR CONSOLE --------------------- #

def limpar_console():
    os.system("cls" if os.name == "nt" else "clear")

# ---------------- FUNÇÃO EXCLUIR BANCO DE DADOS ------------------ #

def limpar_banco():
    for arquivo in os.listdir(PASTA_ARQUIVOS):
        caminho_arquivo = os.path.join(PASTA_ARQUIVOS, arquivo)
        if os.path.isfile(caminho_arquivo):
            os.remove(caminho_arquivo)
    alunos.clear()
    notas.clear()
    fila_alunos.clear()
    ras_existentes.clear()
    print("\nBanco de dados limpo com sucesso!\n")

# ----------------------- FUNÇÃO GERAR RA  ------------------------- #

def gerar_ra():
    while True:
        resto_ra = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        ra = "F" + resto_ra
        if ra not in ras_existentes:
            return ra

# --------------------- FUNÇÃO PRINCIPAL (MENU) --------------------- #

def Menu_Inicial():
    print("""
=============================================
      BEM-VINDO AO SISTEMA ESCOLAR
=============================================

Escolha uma opção para executar:

 [1] 💻 Registrar Aluno No Sistema.
 [2] ✏️ Cadastrar Notas.
 [3] 📊 Consultar Boletim Completo.
 [4] 🎓 Consultar Alunos Cadastrados.
 [5] ❌ Limpar Banco de Dados.
 [6] 👧 Remover Aluno do Sistema.
 [7] 💾 Sair do Sistema.

=============================================
""")
    opcao = input("Opção: ").strip()
    if not opcao.isdigit():
        print("\nPor favor, digite apenas números!\n")
        limpar_console()
        return

    if opcao == "1":
        limpar_console()
        registrar_aluno()
    elif opcao == "2":
        limpar_console()
        cadastrar_notas()
    elif opcao == "3":
        limpar_console()
        consultar_boletim() 
    elif opcao == "4":
        limpar_console()
        listar_alunos()
    elif opcao == "5":
        limpar_console()
        print("""
=========================================
        ⚠️ ATENÇÃO: LIMPAR BANCO ⚠️
=========================================
""")
        opcao_conf = input("❌ Tem certeza que deseja limpar todo o banco de dados? Essa ação não poderá ser desfeita! (Sim/Não): ").strip()
        if opcao_conf.lower() == "sim":
            senha_correta = "Gabriel123"
            senha = input("Digite a senha para confirmar a exclusão do banco de dados: ").strip()
            if senha == senha_correta:
                limpar_banco()
                input("Banco de Dados deletado com exito! Pressione qualquer tecla para retornar.")
                limpar_console()
                Menu_Inicial()
            else:
                input("Senha incorreta! Operação cancelada. Pressione qualquer tecla para retornar.")
                limpar_console()
                Menu_Inicial()
        else:
            limpar_console()
            Menu_Inicial()
    elif opcao == "6":
        remover_aluno()
    elif opcao == "7":
        print("Saindo do sistema...")
        limpar_console()
        exit()
    else:
        print("Opção inválida! Tente novamente.")
        Menu_Inicial()

# --------------------- REGISTRO DE ALUNOS --------------------- #

def registrar_aluno():
    while True:
        print("""
=========================================
   ✨ REGISTRO DE ALUNO NO SISTEMA ✨
=========================================
""")
        nome = input("🧑 Digite o nome do aluno: ").strip().capitalize()
        if not nome.replace(" ", "").isalpha():
            print("\nDigite apenas letras.\n")
            continue

        turmas_disponiveis = ["9A", "9B", "9C"]
        turma = input("🎓 Digite a turma do aluno: ").strip().upper()
        if turma not in turmas_disponiveis:
            print(f"\nTurma inválida! Disponíveis: {', '.join(turmas_disponiveis)}")
            continue

        ra = gerar_ra()
        print(f"RA gerado automaticamente: {ra}")

        alunos[ra] = {"nome": nome, "turma": turma}
        fila_alunos.append(ra)
        ras_existentes.add(ra)
        limpar_console()
        salvar_dados()

        print(f"""
=========================================
       ✅ ALUNO CADASTRADO COM SUCESSO ✅
=========================================

🧑 Nome : {nome}
🆔 RA   : {ra}
🎓 Turma: {turma}

=========================================
""")
        menu = input("Pressione ENTER para cadastrar outro aluno ou digite SAIR para voltar ao menu: ").strip()
        if menu.lower() == "sair":
            limpar_console()
            salvar_dados()
            Menu_Inicial()
        elif menu == "":
            limpar_console()
            salvar_dados()
            registrar_aluno()



# --------------------- REGISTRO DE NOTAS --------------------- #

def cadastrar_notas():
    print("""
=========================================
        📝 OPÇÕES DE CADASTRO DE NOTAS
=========================================

[1] 💻 Cadastrar notas por RA
[2] 🏫 Cadastrar notas por Sala (selecionar aluno da turma)
[3] 🔙 Retornar ao menu principal

=========================================
""")
    escolha = input("Escolha uma opção: ").strip()

    # ---------------- CADASTRAR POR RA ---------------- #

    if escolha == "1":
        ra = input("Digite o RA do aluno: ").upper()
        if ra not in alunos:
            print("\nAluno não encontrado! Cadastre-o primeiro.\n")
            input("Pressione qualquer tecla para continuar...")
            limpar_console()
            return 
        cadastrar_notas_individual(ra)
    
    # ---------------- CADASTRAR POR SALA ---------------- #

    elif escolha == "2":
        turmas_disponiveis = sorted({info["turma"] for info in alunos.values()})
        if not turmas_disponiveis:
            print("\nNão há alunos cadastrados ainda.\n")
            return

        print("\nTurmas disponíveis:", ", ".join(turmas_disponiveis))
        turma = input("Digite a turma desejada: ").strip().upper()
        if turma not in turmas_disponiveis:
            print("\nTurma inválida!\n")
            return
        
        alunos_turma = [ra for ra, info in alunos.items() if info["turma"] == turma]
        print(f"\nAlunos da turma {turma}:")
        print("\nRA | ALUNO")
        for ra in alunos_turma:
            print(f"{ra} - {alunos[ra]['nome']}")

        while True:
            ra = input("\nDigite o RA do aluno que deseja cadastrar nota (ou SAIR para voltar): ").upper()
            if ra.lower() == "sair":
                limpar_console()
                salvar_dados()
                Menu_Inicial()
                return
            elif ra not in alunos_turma:
                print("RA inválido ou não pertence a essa turma.")
                continue
            else:
                cadastrar_notas_individual(ra)
    
    # ---------------- VOLTAR AO MENU ---------------- #

    elif escolha == "3":
        limpar_console()
        Menu_Inicial()
    
    else:
        print("\nOpção inválida!\n")
        cadastrar_notas()

# --------------------- FUNÇÃO AUXILIAR PARA CADASTRAR NOTAS --------------------- #

def cadastrar_notas_individual(ra):
    if ra not in alunos:
        print("\nRA não encontrado. Cadastre o aluno primeiro!\n")
        input("Pressione qualquer tecla para voltar...")
        limpar_console()
        return
    
    while True:
        print(f"""
=========================================
          📝 CADASTRO DE NOTAS
=========================================

Escolha a matéria para o aluno:

[1] 🧮 Matemática
[2] ✏️ Português
[3] 📜 História
[4] 🌍 Geografia

-----------------------------------------
Aluno: {alunos[ra]['nome']} | Turma: {alunos[ra]['turma']}
=========================================
""")

        materia_input = input("Matéria (número): ").strip()
        materias = {1: "Matematica", 2: "Portugues", 3: "Historia", 4: "Geografia"}
        if not materia_input.isdigit() or int(materia_input) not in materias:
            print("\nOpção inválida!\n")
            return

        materia = materias[int(materia_input)]

        try:
            n1 = float(input("Nota N1: "))
            n2 = float(input("Nota N2: "))
            if n1 > 10 or n2 > 10:
                print("Nota inválida, deve ser 0-10.")
                continue
        except ValueError:
            print("\nDigite apenas números para as notas.\n")
            return

        media = (n1 + n2) / 2
        if ra not in notas:
            notas[ra] = {}
        notas[ra][materia] = media
        print(f"\nA média em {materia} do aluno {alunos[ra]['nome']} é: {media:.2f}")
        salvar_dados()

        menu = input("\nPressione ENTER para cadastrar outra nota para este aluno, ou digite SAIR para voltar: ")
        if menu.lower() == "sair":
            Menu_Inicial()
            limpar_console()
        else:
            cadastrar_notas_individual(ra)



# --------------------- CONSULTAR BOLETIM --------------------- #

def consultar_boletim():
    print("""
=========================================
      📊 CONSULTAR BOLETIM DO ALUNO
=========================================
""")
    ra = input("🆔 Digite o RA do aluno: ").strip().upper()
    limpar_console()
    if ra not in alunos:
        print("\nRA não encontrado.\n")
        input("Pressione qualquer tecla para voltar...")
        limpar_console()
        Menu_Inicial()
        return

    info = alunos[ra]
    print(f"""
=========================================
         BOLETIM DE {info['nome'].upper()}
=========================================

🧑 Nome : {info['nome']}
🆔 RA   : {ra}
🎓 Turma: {info['turma']}
-----------------------------------------
""")

    if ra in notas and notas[ra]:
        soma_geral = 0
        qtd_materias = 0
        print("📌 Notas por matéria:\n")
        for materia, media in notas[ra].items():
            print(f"   {materia:<12} : {media:.2f}")
            soma_geral += media
            qtd_materias += 1

        media_geral = soma_geral / qtd_materias
        status = "APROVADO ✅" if media_geral >= 6 else "REPROVADO ❌"

        print("\n=========================================")
        print(f"        MÉDIA GERAL : {media_geral:.2f}")
        print(f"        STATUS      : {status}")
        print("=========================================\n")
    else:
        print("Nenhuma nota cadastrada ainda.\n")

    input("Pressione qualquer tecla para continuar...")
    limpar_console()
    Menu_Inicial()



# --------------------- LOOP PRINCIPAL --------------------- #
carregar_dados()
while True:
    Menu_Inicial()
