# By Gabriel Schmeisk

from collections import deque  # Importa deque, usado para criar filas que permitem adicionar/remover elementos dos dois lados
import os                      # Importa o módulo OS para manipulação de arquivos e pastas
import random                  # Importa random, utilizado para gerar RAs aleatórios
import string                  # Importa string, utilizado para gerar letras e números para o RA

# --------------------- DICIONÁRIOS E FILAS --------------------- #
alunos = {}             # Dicionário que guarda os alunos cadastrados. Chave: RA, Valor: {"nome": ..., "turma": ...}
notas = {}              # Dicionário que guarda as notas dos alunos. Chave: RA, Valor: {"materia": media, ...}
fila_alunos = deque()   # Fila para controlar a ordem dos alunos, útil para salvar na ordem de cadastro
ras_existentes = set()  # Conjunto que guarda os RAs existentes, garantindo que não haja duplicados

# --------------------- CRIAÇÃO DE PASTAS --------------------- #
PASTA_ARQUIVOS = "dados_escolares"      # Define o nome da pasta principal onde serão salvos arquivos de alunos e notas
if not os.path.exists(PASTA_ARQUIVOS):  # Verifica se a pasta já existe
    os.makedirs(PASTA_ARQUIVOS)         # Se não existir, cria a pasta

PASTA_TURMAS = "turmas"               # Define a pasta onde cada turma terá seu arquivo separado
if not os.path.exists(PASTA_TURMAS):  # Verifica se a pasta de turmas existe
    os.makedirs(PASTA_TURMAS)         # Cria a pasta caso não exista

# --------------------- VALIDAÇÃO DE MATÉRIAS --------------------- #
def obter_materias_validas():
    # Função que retorna uma lista com as matérias válidas do sistema
    return ["Matematica", "Portugues", "Historia", "Geografia"]

# --------------------- VALIDAÇÃO DE MATÉRIAS --------------------- #
def sair():
    # Função que retorna uma lista com as matérias válidas do sistema
    return ["sair", "sai", "sa", "voltar", "volta", "leave"]

# --------------------- VALIDAÇÃO DE TURMAS --------------------- #

def turmasfixas():
    # Função que retorna as turmas válidas
    return ["9A", "9B", "9C"]

# --------------------- FUNÇÃO PARA CARREGAR DADOS --------------------- #
def carregar_dados():
    # Monta o caminho completo do arquivo "alunos.txt" que está dentro da pasta definida em PASTA_ARQUIVOS
    arquivo_alunos = os.path.join(PASTA_ARQUIVOS, "alunos.txt")

    try:
        # Abre o arquivo de alunos em modo leitura ("r") usando codificação UTF-8
        with open(arquivo_alunos, "r", encoding="utf-8") as f:
            ra_atual = None  # Variável que guarda temporariamente o RA do aluno que está sendo lido

            # Percorre cada linha do arquivo "alunos.txt"
            for linha in f:
                linha = linha.strip()  # Remove espaços em branco extras no início e no fim da linha

                # Caso a linha comece com "Aluno:", significa que ela contém informações de um aluno
                if linha.startswith("Aluno:"):
                    partes = linha.split("|")  # Divide a linha em partes separadas pelo caractere "|"

                    # Divide o nome em 2 partes antes e depois do :

                    nome = partes[0].split(":", 1)[1].strip()
                    # "Aluno: Gabriel Schmeisk".split(":", 1)
                    # Resultado: ["Aluno", " Gabriel Schmeisk"]
                
                    ra = partes[1].split(":", 1)[1].strip().upper()


                    turma = partes[2].split(":", 1)[1].strip()

                    # Salva os dados do aluno em um dicionário global chamado "alunos"
                    # Estrutura: alunos[RA] = { "nome": nome_do_aluno, "turma": turma_do_aluno }
                    alunos[ra] = {"nome": nome, "turma": turma}

                    # Verifica se o RA já não está na fila de alunos
                    if ra not in fila_alunos:
                        fila_alunos.append(ra)   # Adiciona o RA na fila (ordem de leitura/cadastro)
                        ras_existentes.add(ra)   # Guarda o RA em um conjunto para evitar duplicatas
                        ra_atual = ra            # Atualiza o "ra_atual" para saber de quem são as notas a seguir
                        continue                 # Pula para a próxima linha do arquivo

                # Caso a linha contenha ":" e não seja a linha da "Média geral"
                # Isso indica que estamos lendo as notas de um aluno
                if ":" in linha and ra_atual and not linha.startswith("Média geral"):

                    # Garante que o aluno atual tenha um dicionário de notas criado
                    notas[ra_atual] = notas.setdefault(ra_atual, {})

                    # Cada linha de notas pode conter várias matérias separadas por "|"
                    for parte in linha.split("|"):
                        if ":" in parte:  # Verifica se a parte contém "matéria: nota"
                            materia, media = parte.split(":", 1)  # Divide em nome da matéria e a nota
                            materia, media = materia.strip(), media.strip()  # Remove espaços extras

                            # Ignora se a "matéria" for a média geral (pois será calculada separadamente)
                            if materia.lower() != "média geral":
                                if media.upper() == "N/A":  # Caso a nota seja "N/A", significa que não existe
                                    notas[ra_atual][materia] = None
                                else:
                                    try:
                                        # Converte a nota para número decimal (float)
                                        notas[ra_atual][materia] = float(media)
                                    except ValueError:
                                        # Caso a conversão falhe (valor inválido), define como None
                                        notas[ra_atual][materia] = None

    # Caso o arquivo "alunos.txt" não exista ainda (primeira execução do sistema)
    except FileNotFoundError:
        pass  # Apenas ignora, não gera erro, pois significa que ainda não há alunos cadastrados

    # Após carregar todos os alunos e suas notas, atualiza os arquivos de turmas
    salvar_turmas()




# --------------------- FUNÇÃO PARA SALVAR DADOS --------------------- #
def salvar_dados():
    # Monta o caminho completo do arquivo "alunos.txt" dentro da pasta PASTA_ARQUIVOS.
    arquivo_alunos = os.path.join(PASTA_ARQUIVOS, "alunos.txt")  # caminho do arquivo onde serão gravados os dados

    # Abre o arquivo em modo escrita ("w") com codificação UTF-8.
    # Modo "w" sobrescreve totalmente o arquivo existente — cuidado se quiser apenas acrescentar.
    # O context manager (with) garante que o arquivo seja fechado automaticamente ao final (mesmo em erro).
    with open(arquivo_alunos, "w", encoding="utf-8") as f:
        # Escreve um cabeçalho fixo de direitos e ano na primeira linha do arquivo.
        f.write("© Todos os direitos reservados TecMais LTDA - 2025\n")

        # Escreve uma linha separadora (60 sinais de "=") e pula uma linha.
        f.write("=" * 60 + "\n\n")

        # Se o dicionário 'alunos' estiver vazio (nenhum aluno cadastrado)
        if not alunos:
            # Escreve uma mensagem indicando que não há alunos no sistema
            f.write("❌ Nenhum aluno cadastrado no sistema.\n")
            # Escreve uma linha separadora.
            f.write("-" * 60 + "\n")
        else:
            # Cria um conjunto com todas as turmas (info["turma"] para cada aluno) e ordena alfabeticamente.
            # Isso garante que o arquivo seja organizado por turma em ordem crescente.
            for turma in sorted({info["turma"] for info in alunos.values()}):
                # Escreve o título da turma atual (ex: "===== TURMA A =====")
                f.write(f"===== TURMA {turma} =====\n\n")

                # Monta uma lista com os RAs dos alunos que pertencem à turma atual.
                # alunos.items() retorna pares (ra, info) e filtramos por info["turma"] == turma.
                alunos_turma = [ra for ra, info in alunos.items() if info["turma"] == turma]

                # Ordena a lista de RAs da turma pelo nome do aluno (alunos[ra]["nome"]).
                # Assim a saída na turma fica em ordem alfabética de nome.
                alunos_turma.sort(key=lambda ra: alunos[ra]["nome"])

                # Flag que indica se ao menos um aluno da turma tem nota cadastrada.
                turma_tem_notas = False

                # Percorre cada RA dos alunos daquela turma para escrever seus dados e notas.
                for ra in alunos_turma:
                    info = alunos[ra]  # Dicionário com chaves "nome" e "turma"
                    # Escreve a linha principal do aluno: nome, RA e turma.
                    f.write(f"Aluno: {info['nome']} | RA: {ra} | Turma: {info['turma']}\n")

                    # Obtém as notas do aluno a partir do dicionário global 'notas'.
                    # Se o RA não existir em 'notas', usamos um dicionário vazio como padrão para não gerar erro.
                    notas_aluno = notas.get(ra, {})

                    # Flag que será False se alguma matéria estiver sem nota (N/A).
                    todas_as_notas = True
                    # Flag que indica se o aluno tem ao menos uma nota cadastrada (diferente de N/A).
                    aluno_tem_nota = False

                    # Percorre cada matéria válida (função obter_materias_validas() deve retornar lista/iterável).
                    # Para cada matéria, escreve "Matéria: valor | " ou "Matéria: N/A | ".
                    for materia in obter_materias_validas():
                        # Se a matéria existe no dicionário do aluno e o valor não é None, escrevemos a nota.
                        if materia in notas_aluno and notas_aluno[materia] is not None:
                            # Formata a nota com duas casas decimais (ex: 7.50)
                            f.write(f"{materia}: {notas_aluno[materia]:.2f} | ")
                            aluno_tem_nota = True  # marcou que esse aluno tem pelo menos uma nota válida
                        else:
                            # Caso contrário, escreve N/A e marca que nem todas as notas estão presentes
                            f.write(f"{materia}: N/A | ")
                            todas_as_notas = False

                    # Se o aluno teve pelo menos uma nota, a turma passa a ter notas também.
                    if aluno_tem_nota:
                        turma_tem_notas = True

                    # Cálculo da média geral: só é feito se todas as matérias tiverem nota (todas_as_notas True)
                    # e se o aluno efetivamente tiver alguma nota (aluno_tem_nota True).
                    if todas_as_notas and aluno_tem_nota:
                        # Soma as notas para todas as matérias válidas e divide pelo número de matérias.
                        # OBS: aqui o código chama obter_materias_validas() novamente — ver observação de otimização abaixo.
                        media_geral = sum(notas_aluno[m] for m in obter_materias_validas()) / len(obter_materias_validas())
                        f.write(f"Média geral: {media_geral:.2f}\n")
                    else:
                        # Se faltar alguma nota, escreve "Média geral: N/A"
                        f.write("Média geral: N/A\n")

                    # Linha separadora após os dados do aluno
                    f.write("-" * 60 + "\n")

                # Se, após verificar todos os alunos da turma, nenhum possuía nota válida, escreve aviso.
                if not turma_tem_notas:
                    f.write("❌ Nenhuma nota cadastrada nessa turma.\n")
                    f.write("-" * 60 + "\n")


     # ------------------- Cria arquivos separados por matéria -------------------
    # Aqui o sistema vai gerar um arquivo .txt para cada matéria cadastrada no sistema.
    # Exemplo: "matematica.txt", "portugues.txt", etc.
    for materia in obter_materias_validas():
        # Converte o nome da matéria para minúsculas e adiciona ".txt"
        nome_arquivo = materia.lower() + ".txt"

        # Monta o caminho completo do arquivo juntando a pasta e o nome do arquivo
        caminho_completo = os.path.join(PASTA_ARQUIVOS, nome_arquivo)

        # Abre o arquivo em modo escrita ("w"), ou seja, sobrescreve se já existir.
        with open(caminho_completo, "w", encoding="utf-8") as f_mat:
            # Escreve o cabeçalho fixo da TecMais LTDA com ano
            f_mat.write("© Todos os direitos reservados TecMais LTDA - 2025\n")
            # Linha separadora de 60 "="
            f_mat.write("=" * 60 + "\n\n")
            # Escreve o título com o nome da matéria
            f_mat.write(f"===== Notas de {materia} =====\n\n")

            # Flag que indica se algum aluno possui nota nessa matéria
            materia_tem_nota = False

            # Percorre os alunos na ordem da fila (fila_alunos preserva a ordem de cadastro/carregamento)
            for ra in fila_alunos:
                info = alunos[ra]  # Recupera informações do aluno (nome e turma)
                # Busca a nota da matéria para o aluno. Se não existir, retorna None.
                nota = notas.get(ra, {}).get(materia)

                if nota is not None:
                    # Caso o aluno tenha nota, escreve a linha com os dados e a nota formatada com 2 casas decimais
                    f_mat.write(
                        f"Aluno: {info['nome']} | RA: {ra} | Turma: {info['turma']} | Nota: {nota:.2f}\n"
                        + "-" * 60 + "\n"
                    )
                    # Marca que essa matéria tem pelo menos uma nota cadastrada
                    materia_tem_nota = True
                else:
                    # Caso o aluno não tenha nota cadastrada (ou seja None)
                    f_mat.write(
                        f"Aluno: {info['nome']} | RA: {ra} | Turma: {info['turma']} | Nota: N/A\n"
                        + "-" * 60 + "\n"
                    )

            # Se após percorrer todos os alunos, nenhum tinha nota nessa matéria:
            if not materia_tem_nota:
                f_mat.write("❌ Nenhuma nota cadastrada para esta matéria.\n")
                f_mat.write("-" * 60 + "\n")

    # Exibe no terminal uma mensagem de sucesso ao finalizar todo o processo
    print("\nBanco de dados atualizado com sucesso!!\n")


# --------------------- FUNÇÃO PARA SALVAR TURMAS --------------------- #
def salvar_turmas():
    # Cria a pasta de turmas, se não existir
    if not os.path.exists(PASTA_TURMAS):
        os.makedirs(PASTA_TURMAS)

    turmas = {}

    # Agrupa alunos existentes no dicionário "alunos"
    for ra, dados in alunos.items():
        # Normaliza o nome da turma para MAIÚSCULAS (garante chave única independente de maiúsc/minúsc)
        turma = dados["turma"].upper()
        # Usa setdefault para criar a lista se não existir e depois acrescenta uma tupla (ra, nome)
        turmas.setdefault(turma, []).append((ra, dados["nome"]))

    # Remove arquivos de turmas que não existem mais e não são fixas
    #for arquivo in os.listdir(PASTA_TURMAS):
        #nome_turma = arquivo.replace(".txt", "")
        # Se o nome da turma não estiver na lista atual de turmas e também não for uma turma fixa, remove o arquivo
        #if nome_turma not in turmas and nome_turma not in turmasfixas():
           # os.remove(os.path.join(PASTA_TURMAS, arquivo))

    # Garante que todas as turmas fixas existam, mesmo sem alunos
    for turma in turmasfixas():
        caminho_arquivo = os.path.join(PASTA_TURMAS, f"{turma}.txt")
        # Se a turma fixa não existir na lista de turmas ou estiver vazia, cria um arquivo com cabeçalho e mensagem
        if turma not in turmas or not turmas[turma]:
            with open(caminho_arquivo, "w", encoding="utf-8") as f:
                f.write("© Todos os direitos reservados TecMais LTDA - 2025\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"===== TURMA {turma} =====\n\n")
                f.write("Nenhum aluno cadastrado nesta turma.\n")

    # Atualiza arquivos de turmas
    for turma, lista_alunos in turmas.items():
        caminho_arquivo = os.path.join(PASTA_TURMAS, f"{turma}.txt")
        if lista_alunos:
            # Turma com alunos: sobrescreve arquivo
            soma_medias, qtd_com_nota = 0, 0
            with open(caminho_arquivo, "w", encoding="utf-8") as f:
                f.write("© Todos os direitos reservados TecMais LTDA - 2025\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"===== TURMA {turma} =====\n\n")
                for ra, nome in lista_alunos:
                    f.write(f"Aluno: {nome} | RA: {ra} | Turma: {turma}\n")
                    notas_aluno = notas.get(ra, {})
                    # Verifica se o aluno tem todas as matérias com nota válida
                    if all(materia in notas_aluno and notas_aluno[materia] is not None for materia in obter_materias_validas()):
                        media_individual = sum(notas_aluno[materia] for materia in obter_materias_validas()) / len(obter_materias_validas())
                        soma_medias += media_individual
                        qtd_com_nota += 1
                        f.write(f"   Média do aluno: {media_individual:.2f}\n")
                    else:
                        f.write("   Média do aluno: N/A\n")
                    f.write("-" * 50 + "\n")

                # Média da turma
                if qtd_com_nota > 0:
                    media_turma = soma_medias / qtd_com_nota
                    f.write(f"\n📊 MÉDIA DA TURMA {turma}: {media_turma:.2f}\n")
                else:
                    f.write("\n❌ Nenhum aluno possui todas as notas para calcular a média da turma.\n")
        else:
            # Turma sem alunos e não fixa: apaga arquivo
            if turma not in turmasfixas() and os.path.exists(caminho_arquivo):
                os.remove(caminho_arquivo)


# --------------------- FUNÇÃO PARA LISTAR ALUNOS --------------------- #
def listar_alunos():

    # Verifica se não há alunos cadastrados no dicionário global "alunos"
    if not alunos:
        # Exibe mensagem de aviso e pausa até o usuário pressionar alguma tecla
        input("\n❌ Nenhum aluno cadastrado ainda. Pressione qualquer tecla para continuar.\n")
        return

    # Cabeçalho da listagem de alunos por turma
    print("\n===== ALUNOS POR TURMA =====\n")

    # Cria uma lista de turmas únicas a partir do dicionário de alunos e ordena alfabeticamente
    turmas = sorted({info["turma"] for info in alunos.values()})

    # Percorre cada turma para listar os alunos
    for turma in turmas:
        print(f"--- Turma {turma} ---")  # Título da turma

        # Filtra os RAs dos alunos pertencentes à turma atual
        ras_turma = [ra for ra, info in alunos.items() if info["turma"] == turma]

        # Ordena os RAs com base no nome do aluno para exibição ordenada
        ras_turma.sort(key=lambda ra: alunos[ra]["nome"])

        # Percorre cada RA da turma
        for ra in ras_turma:
            info = alunos[ra]  # Recupera informações do aluno

            # Verifica se todas as matérias possuem notas lançadas
            notas_disponiveis = "Sim" if ra in notas and all(
                m in notas[ra] and notas[ra][m] is not None for m in obter_materias_validas()
            ) else "Não"

            # Exibe os dados do aluno e se a média está lançada
            print(f"Nome: {info['nome']} | RA: {ra} | Média Lançada: {notas_disponiveis}")
            print()

    # Linha de separação no final da listagem
    print("=======================================\n")

    # Pausa para o usuário visualizar as informações
    input("Pressione qualquer tecla para continuar.")
    return



# --------------------- FUNÇÃO PARA REMOVER ALUNOS --------------------- #
def remover_alunos():
    while True:  # Loop para permitir tentar novamente caso haja erro ou RA inválido
        # Cabeçalho da operação
        print("""
=========================================
       ❌ REMOVER ALUNO DO SISTEMA ❌
=========================================
""")

        # Solicita RA do aluno ou palavra-chave para voltar
        ra = input("🆔 Digite o RA do aluno que deseja remover (ou VOLTAR para retornar ao menu): ").strip().upper()

        # Permite retornar ao menu principal se o usuário digitar uma opção de saída
        if ra.lower() in sair():
            limpar_console()
            return

        # Verifica se o RA digitado existe no dicionário de alunos
        if ra not in alunos:
            input("\n❌ Aluno não encontrado! Tente novamente.\n")
            limpar_console()
            continue  # Volta para o início do loop para tentar novamente

        # Exibe os dados do aluno para confirmação antes da remoção
        print(f"""
=========================================
       ❌ REMOVER ALUNO DO SISTEMA ❌
    Essa ação não poderá ser desfeita!
=========================================

🧑 Nome : {alunos[ra]['nome']}
🆔 RA   : {ra}
🎓 Turma: {alunos[ra]['turma']}

=========================================
""")

        # Pergunta se o usuário confirma a exclusão
        confirmar = input(f"\nTem certeza que deseja remover {alunos[ra]['nome']} do sistema? (sim/não): ").strip().lower()

        if confirmar == "sim":
            # Senha fixa para permitir exclusão
            senha_correta = "aluno123"
            senha = input("Digite a senha para confirmar a exclusão do aluno: ").strip()

            if senha == senha_correta:
                # Remove aluno de todas as estruturas de dados
                alunos.pop(ra)
                notas.pop(ra, None)
                if ra in fila_alunos:
                    fila_alunos.remove(ra)
                if ra in ras_existentes:
                    ras_existentes.remove(ra)

                # Atualiza os arquivos de dados
                salvar_dados()
                salvar_turmas()
                limpar_console()
                input("\n✅ Aluno removido com sucesso! Pressione qualquer tecla para retornar.")
                return
            else:
                limpar_console()
                input("❌ Senha incorreta! Operação cancelada. Pressione qualquer tecla para retornar.")
                return

        elif confirmar == "não":
            limpar_console()
            input("\n❌ Operação cancelada pelo usuário. Nenhum arquivo foi removido. Pressione qualquer tecla para continuar!")
            return

        else:
            # Caso a opção digitada seja inválida
            limpar_console()
            input("\n❌ Opção inválida, tente novamente!")
            # O loop continua automaticamente para tentar novamente


# --------------------- FUNÇÃO PARA LIMPAR CONSOLE --------------------- #
def limpar_console():
    os.system("cls" if os.name == "nt" else "clear")  # Comando para limpar tela no Windows ou Linux/Mac

# --------------------- FUNÇÃO PARA LIMPAR BANCO DE DADOS --------------------- #
def limpar_banco():
    # Cabeçalho de alerta no console, avisando que esta ação é irreversível
    print("""
=========================================
        ⚠️ ATENÇÃO: LIMPAR BANCO ⚠️
=========================================
""")

    # Solicita confirmação do usuário antes de prosseguir
    opcao_conf = input(
        "❌ Tem certeza que deseja limpar todo o banco de dados? "
        "Essa ação não poderá ser desfeita! (sim/não): "
    ).strip()

    # Se o usuário confirma a operação
    if opcao_conf.lower() == "sim":
        senha_correta = "Gabriel123"  # Senha fixa para segurança
        # Solicita a senha para confirmar a exclusão
        senha = input("Digite a senha para confirmar a exclusão do banco de dados: ").strip()

        # Valida se a senha está correta
        if senha == senha_correta:
            # Percorre todos os arquivos da pasta principal (onde ficam os alunos e notas)
            for arquivo in os.listdir(PASTA_ARQUIVOS):
                caminho_arquivo = os.path.join(PASTA_ARQUIVOS, arquivo)
                # Remove apenas arquivos (ignora pastas)
                if os.path.isfile(caminho_arquivo):
                    os.remove(caminho_arquivo)

            # Percorre todos os arquivos da pasta de turmas
            for arquivo in os.listdir(PASTA_TURMAS):
                caminho_arquivo = os.path.join(PASTA_TURMAS, arquivo)
                # Remove apenas arquivos (ignora pastas)
                if os.path.isfile(caminho_arquivo):
                    os.remove(caminho_arquivo)

            # Limpa todas as estruturas de dados na memória para garantir que nada fique carregado
            alunos.clear()          # Dicionário de alunos
            notas.clear()           # Dicionário de notas
            fila_alunos.clear()     # Fila de alunos para ordem de cadastro
            ras_existentes.clear()  # Conjunto de RAs já existentes

            # Mensagem de sucesso no console
            print("\n✅ Banco de dados limpo com sucesso!\n")
            input("Pressione qualquer tecla para retornar.")
            return

        else:
            # Caso a senha esteja incorreta, cancela a operação
            input("❌ Senha incorreta! Operação cancelada. Pressione qualquer tecla para retornar.")
            return

    # Caso o usuário escolha "não" na confirmação inicial
    elif opcao_conf.lower() == "não":
        input("\n❌ Operação cancelada pelo usuário. Nenhum arquivo foi removido. Pressione qualquer tecla para continuar!")
        limpar_console()
        return

    # Caso o usuário digite algo diferente de "sim" ou "não"
    else:
        input("\n❌ Opção inválida, tente novamente!")
        limpar_console()
        # Chama a própria função novamente para permitir nova tentativa
        limpar_banco()


# --------------------- FUNÇÃO PARA GERAR RA --------------------- #
def gerar_ra():
    while True:  # Loop até gerar RA único
        resto_ra = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))  # 5 caracteres aleatórios
        ra = "F" + resto_ra  # Prefixo F + caracteres aleatórios
        if ra not in ras_existentes:  # Garante que não exista duplicado
            return ra  # Retorna RA único

# --------------------- MENU PRINCIPAL --------------------- #
def menu_inicial():
    print("""
=============================================
      BEM-VINDO AO SISTEMA ESCOLAR
=============================================

Escolha uma opção para executar:

 [1] 💻 Registrar Aluno No Sistema.
 [2] ✏️ Cadastrar Notas.
 [3] 📊 Consultar Boletim Completo.
 [4] 🎓 Consultar Alunos Cadastrados.
 [5] 👧 Remover Aluno do Sistema.
 [6] ❌ Limpar Banco de Dados.
 [7] 💾 Sair do Sistema.

=============================================
""")  # Menu principal
    opcao = input("Opção: ").strip()  # Solicita escolha do usuário
    if not opcao.isdigit():  # Verifica se é número
        limpar_console()
        return

    # Verifica cada opção e chama a função correspondente
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
        remover_alunos()
    elif opcao == "6":
        limpar_console()
        limpar_banco()
    elif opcao == "7":
        print("Saindo do sistema...")
        salvar_dados()  # Salva dados antes de sair
        salvar_turmas()  # Salva turmas antes de sair
        limpar_console()
        exit()
    else:
        print("Opção inválida! Tente novamente.")
        limpar_console()


# --------------------- REGISTRO DE ALUNOS --------------------- #
def registrar_aluno():
    while True:  # Loop para permitir cadastrar vários alunos
        print("""
=========================================
   ✨ REGISTRO DE ALUNO NO SISTEMA ✨
=========================================
""")  # Cabeçalho do registro de alunos

        # --- Entrada e validação do nome ---
        nome = input("🧑 Digite o nome do aluno (ou VOLTAR para retornar ao menu): ").strip().title()  
        if nome.lower() in sair():  # Permite retornar ao menu principal
            limpar_console()
            break  # Encerra a função e volta ao menu principal

        if not nome.replace(" ", "").isalpha():  # Verifica se o nome contém apenas letras
            print("\n❌ Digite apenas letras.\n")
            limpar_console()
            continue  # Reinicia loop se o nome for inválido

        # --- Entrada e validação da turma ---
        turma = input("🎓 Digite a turma do aluno (ou VOLTAR para retornar ao menu): ").strip().upper()  
        if turma.lower() in sair():  # Permite retornar ao menu principal
            limpar_console()
            break

        if turma not in turmasfixas():  # Verifica se a turma digitada é válida
            limpar_console()
            print(f"\n❌ Turma inválida! Disponíveis: {', '.join(turmasfixas())}")
            continue  # Reinicia o loop se a turma não for válida

        # --- Registro do aluno ---
        ra = gerar_ra()  # Gera RA único para o aluno
        alunos[ra] = {"nome": nome, "turma": turma}  # Adiciona o aluno ao dicionário principal
        fila_alunos.append(ra)  # Coloca o RA na fila
        ras_existentes.add(ra)  # Adiciona o RA ao conjunto de RAs já cadastrados
        salvar_dados()  # Salva os dados no arquivo principal
        salvar_turmas()  # Salva os dados separados por turma
        limpar_console()  # Limpa a tela para mostrar mensagem de sucesso

        # --- Mensagem de confirmação ---
        print(f"""
=========================================
       ✅ ALUNO CADASTRADO COM SUCESSO ✅
=========================================

🧑 Nome : {nome}
🆔 RA   : {ra}
🎓 Turma: {turma}

=========================================
""")  # Exibe os dados do aluno cadastrado

        # --- Opção para cadastrar mais ou retornar ---
        menu = input("Pressione ENTER para cadastrar outro aluno ou digite VOLTAR para retornar ao menu: ").strip().lower()
        if menu.lower() in sair():  # Permite sair do cadastro
            limpar_console()
            break


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
""")  # Menu de cadastro de notas
    escolha = input("Escolha uma opção: ").strip()  # Solicita escolha

    # ---------------- CADASTRAR POR RA ---------------- #
    if escolha == "1":
        limpar_console()
        ra = input("Digite o RA do aluno: ").strip().upper()  # Solicita RA
        if ra not in alunos:  # Verifica se aluno existe
            limpar_console()
            print("\n❌ Aluno não encontrado! Cadastre-o primeiro.\n")
            input("Pressione qualquer tecla para continuar...")
            limpar_console()
            return 
        cadastrar_notas_individual(ra)  # Chama função de cadastro individual

    # ---------------- CADASTRAR POR SALA ---------------- #
    elif escolha == "2":
        turmas_disponiveis = sorted({info["turma"] for info in alunos.values()})  # Lista turmas existentes
        if not turmas_disponiveis:  # Verifica se há alunos cadastrados
            limpar_console()
            input("\n❌ Não há alunos cadastrados ainda. Pressione qualquer tecla para retornar.\n")
            return
        
        limpar_console()
        print("\nTurmas disponíveis:", ", ".join(turmas_disponiveis))
        turma = input("Digite a turma desejada: ").strip().upper()  # Solicita turma
        if turma not in turmas_disponiveis:
            limpar_console()
            print("\nTurma inválida!\n")
            return
        
        alunos_turma = [ra for ra, info in alunos.items() if info["turma"] == turma]  # Filtra alunos da turma

        while True:  # Loop para cadastrar notas de alunos da turma
            limpar_console()
            print(f"\nAlunos da turma {turma}:")
            print("\nRA | ALUNO")
            for ra in alunos_turma:
                print(f"{ra} - {alunos[ra]['nome']}")  # Mostra RA e nome

            ra = input("\nDigite o RA do aluno que deseja cadastrar nota (ou SAIR para voltar): ").strip().upper()
            if ra.lower() in sair():  # Permite sair do loop
                limpar_console()
                salvar_dados()
                salvar_turmas()
                return
            elif ra not in alunos_turma:  # Valida RA
                limpar_console()
                print("\n❌ RA inválido ou não pertence a essa turma.")
                continue
            else:
                cadastrar_notas_individual(ra)  # Chama função de cadastro individual

    # ---------------- VOLTAR AO MENU ---------------- #
    elif escolha == "3":
        limpar_console()
        return
    
    else:
        input("\nOpção inválida!\n")
        limpar_console()
        cadastrar_notas()  # Reinicia função se inválido

# --------------------- FUNÇÃO AUXILIAR PARA CADASTRAR NOTAS --------------------- #
def cadastrar_notas_individual(ra):
    if ra not in alunos:  # Verifica se RA existe
        limpar_console()
        print("\n❌ RA não encontrado. Cadastre o aluno primeiro!\n")
        input("Pressione qualquer tecla para voltar...")
        return
    
    while True:  # Loop para permitir cadastrar várias notas
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
""")  # Menu de seleção de matéria

        materia_input = input("Matéria (número): ").strip()  # Solicita número da matéria
        materias = {1: "Matematica", 2: "Portugues", 3: "Historia", 4: "Geografia"}  # Mapeamento
        if not materia_input.isdigit() or int(materia_input) not in materias:  # Valida entrada
            print("\n❌ Opção inválida!\n")
            return

        materia = materias[int(materia_input)]  # Seleciona matéria correta

        try:
            n1 = float(input(f"Nota N1 de {materia}: "))  # Solicita nota 1
            n2 = float(input(f"Nota N2 de {materia}: "))  # Solicita nota 2
            if n1 > 10 or n2 > 10:  # Valida limite de nota
                print("❌ Nota inválida, deve ser 0-10.")
                continue
        except ValueError:
            print("\nDigite apenas números para as notas.\n")
            return

        media = (n1 + n2) / 2  # Calcula média da matéria
        if ra not in notas:
            notas[ra] = {}  # Cria dicionário de notas se não existir
        notas[ra][materia] = media  # Salva nota
        print(f"\nA média em {materia} do aluno {alunos[ra]['nome']} é: {media:.2f}")
        salvar_dados()  # Atualiza arquivo principal
        salvar_turmas()  # Atualiza arquivos de turmas

        menu = input("\nPressione ENTER para cadastrar outra nota para este aluno, ou digite SAIR para voltar: ").strip()
        if menu.lower() in sair():  # Permite sair do loop
            return
        else:
            cadastrar_notas_individual(ra)  # Permite cadastrar outra nota

# --------------------- CONSULTAR BOLETIM --------------------- #
def consultar_boletim():
    while True:  # Loop para permitir consultar vários boletins
        print("""
=========================================
      📊 CONSULTAR BOLETIM DO ALUNO
=========================================
""")  # Cabeçalho da consulta
        ra = input("🆔 Digite o RA do aluno (ou SAIR para voltar): ").strip().upper()  # Solicita RA
        limpar_console()

        if ra.lower() in sair():  # Permite sair
            return

        if ra not in alunos:  # Valida RA
            print("\n❌ RA não encontrado.\n")
            input("Pressione qualquer tecla para tentar novamente...")
            limpar_console()
            continue  # Repete loop

        info = alunos[ra]  # Pega dados do aluno
        print(f"""
=========================================
         BOLETIM DE {info['nome'].upper()}
=========================================

🧑 Nome : {info['nome']}
🆔 RA   : {ra}
🎓 Turma: {info['turma']}
-----------------------------------------
""")  # Exibe cabeçalho do boletim


        if ra in notas and notas[ra]:  # Verifica se existem notas
            soma_geral = 0  # Soma das médias
            qtd_materias = 0  # Contador de matérias com nota
            print("📌 Notas por matéria:\n")
            
            for materia in obter_materias_validas():
                media = notas[ra].get(materia)  # Pega a nota ou None
                if media is not None:  # Se existe nota válida
                    print(f"   {materia:<12} : {media:.2f}")  # Exibe nota formatada
                    soma_geral += media  # Soma para média geral
                    qtd_materias += 1  # Conta matéria válida
                else:  # Caso não exista nota
                    print(f"   {materia:<12} : N/A")  # Exibe N/A

            # Calcula média geral apenas se todas as matérias tiverem nota
            if qtd_materias == len(obter_materias_validas()):
                media_geral = soma_geral / qtd_materias  # Calcula média geral
                status = "APROVADO ✅" if media_geral >= 6 else "REPROVADO ❌"  # Define status

                print("\n=========================================")
                print(f"        MÉDIA GERAL : {media_geral:.2f}")
                print(f"        STATUS      : {status}")
                print("=========================================\n")
            else:  # Caso faltem notas
                print("\n=========================================")
                print("   STATUS : MATÉRIAS A SEREM LANÇADAS ⏳")
                print("=========================================\n")
        else:  # Se não houver nenhuma nota cadastrada
            print("❌ Nenhuma nota cadastrada ainda.\n")

        input("Pressione qualquer tecla para continuar...")  # Pausa
        limpar_console()  # Limpa console após exibir boletim



# --------------------- LOOP PRINCIPAL --------------------- #

carregar_dados()
salvar_turmas()  # só depois de carregar os alunos
while True:
    limpar_console()
    menu_inicial()
