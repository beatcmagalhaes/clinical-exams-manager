"""
Curso: Mestrado em Bioestatística e Bioinformática Aplicadas à Saúde
Unidade Curricular: Programação e Bases de Dados 
Ano letivo: 2025/2026
Ano: 1º Semestre: 1º


Realizado por:
Andreia Vieira (10250928), Beatriz Magalhães (10250035 / GitHub: @beatcmagalhaes), 
Salvador Caetano Mota (10250931) e Vasco Baldini (10250932 / GitHub: @LewaAir)


Gestor de Exames Clínicos


Objetivo:
    - Gerir exames clínicos de forma simples:
        - Registar
        - Agendar automaticamente
        - Atualizar
        - Eliminar
        
        - Pesquisar
        - Exportar para CSV
        - Ver estado (Aprovado / Pendente)

Tecnologias usadas:
    - Python
    - Tkinter (interface gráfica)
    - JSON (guardar dados)
    - CSV (exportar dados)
"""

import json
import csv
import os
from datetime import datetime, date, timedelta

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# =================== CONFIGURAÇÃO ===================

FICHEIRO_EXAMES = "exames.json"
FORMATO_DATA = "%d-%m-%Y"

# Tipos de exame disponíveis
TIPOS_EXAME = [
    "Raio-X", "Análises", "ECG", "Ressonância", "Ecografia", "TAC",
    "Mamografia", "Endoscopia", "Colonoscopia", "Hemograma", "Urina (EAS)",
    "PCR/Microbiologia", "Prova de Esforço", "Holter", "MAPA"
]

# Capacidade diária máxima para cada tipo de exame (usada como referência)
CAPACIDADE_DIARIA = {
    "Raio-X": 3,
    "Análises": 6,
    "ECG": 2,
    "Ressonância": 3,
    "Ecografia": 4,
    "TAC": 2,
    "Mamografia": 3,
    "Endoscopia": 3,
    "Colonoscopia": 4,
    "Hemograma": 6,
    "Urina (EAS)": 5,
    "PCR/Microbiologia": 5,
    "Prova de Esforço": 4,
    "Holter": 2,
    "MAPA": 2
}

# Horas fixas por tipo de exame (1 "vaga" = 1 hora)
HORAS_POR_TIPO = {
    "Raio-X": ["09:00", "11:00", "15:00"],
    "Análises": ["08:00", "08:30", "09:00", "09:30", "10:00", "10:30"],
    "ECG": ["10:00", "14:00"],
    "Ressonância": ["09:00", "13:00", "16:00"],
    "Ecografia": ["09:00", "10:30", "14:00", "15:30"],
    "TAC": ["09:00", "15:00"],
    "Mamografia": ["10:00", "11:30", "15:00"],
    "Endoscopia": ["09:00", "11:00", "14:00"],
    "Colonoscopia": ["08:30", "10:30", "14:00", "16:00"],
    "Hemograma": ["08:00", "08:15", "08:30", "08:45", "09:00", "09:15"],
    "Urina (EAS)": ["09:00", "09:20", "09:40", "10:00", "10:20"],
    "PCR/Microbiologia": ["10:00", "10:30", "11:00", "11:30", "12:00"],
    "Prova de Esforço": ["09:00", "11:00", "15:00", "16:30"],
    "Holter": ["09:00", "15:00"],
    "MAPA": ["08:30", "14:30"]
}

# Dias de antecedência mínima para marcação (ex.: 2 dias)
dias_antecedencia = 2

# Paleta de cores
BG = "#f5fbf8"        # fundo geral
TOP = "#2f6f5e"       # barra topo
ACCENT = "#9bd1b7"    # destaques
TEXT_DARK = "#154138" # texto principal

# =================== FUNÇÕES AUXILIARES ===================

def data_hoje():
    """Devolve a data de hoje em string com a formatação desejada (dd-mm-yyyy)."""
    hoje = date.today()
    texto = hoje.strftime(FORMATO_DATA)
    return texto


def dia_inicial_marcacao():
    """Primeiro dia possível para marcar exames (hoje + dias_antecedencia)."""
    return date.today() + timedelta(days=dias_antecedencia) #como estamos a ir buscar as datas à biblioteca e elas seguem já um formato definido
                                                            #time delta é para conseguirmos fazer a soma das datas 

def ler_dados():
    """
    Lê os exames do ficheiro JSON.
    Se não existir ou der erro, devolve lista vazia
    """
    if not os.path.exists(FICHEIRO_EXAMES): #vai ler o caminho, o "path" e verifica se é existente se há path que ligue o programa ao .json
        return [] #se não, abre uma lista vazia

    try:
        with open(FICHEIRO_EXAMES, "r", encoding="utf-8") as f: #se existir, tenta ler o ficheiro e ver se não está corrompido
            exames = json.load(f)
            return exames
    except (json.JSONDecodeError, OSError):
        messagebox.showwarning(
            "Aviso",
            "Não foi possível ler o ficheiro de exames. Vai ser iniciada uma lista vazia."
        )
        return []


def gravar_dados(exames):
    """Guarda a lista de exames no ficheiro JSON."""
    try:
        with open(FICHEIRO_EXAMES, "w", encoding="utf-8") as f:
            json.dump(exames, f, ensure_ascii=False, indent=2) #Permite que seja escrito com caracteres especiais e uma indentenção especial
        return True
    except OSError as e:
        messagebox.showerror("Erro", f"Erro ao gravar os dados: {e}")
        return False


def proximo_numero(exames):
    """
    Devolve o próximo número de exame disponível.
    Percorre a lista de exames um a um 
    Procura o maior número existente e soma 1.
    Se não houver exames, começa em 1.
    """
    max_num = 0

    for exame in exames:
        num_str = exame.get("num", 0)
        try:
            num = int(num_str)
        except (TypeError, ValueError):
            num = 0
        if num > max_num:
            max_num = num

    proximo = max_num + 1
    return proximo


def validar_data(texto_data):
    """Verifica se uma data está no formato dd-mm-yyyy e é válida."""
    try:
        datetime.strptime(texto_data, FORMATO_DATA)
        return True
    except ValueError:
        return False


def validar_utente(numero_utente):
    """Verifica se o nº de utente tem só dígitos e entre 9 e 11 caracteres."""
    if not numero_utente.isdigit():
        return False

    tamanho = len(numero_utente)
    if tamanho < 9 or tamanho > 11:
        return False

    return True


def contar_marcados(exames, tipo_exame, data_marcada_str, ignorar_num=None):
    """
    Funciona como uma dupla verificação: conta quantos exames existem de um certo tipo numa certa data.
    Pode ignorar o número de exame se estivermos a editar um exame (para não contar como se fosse um novo). (com o ignorar_num)
    O resultado da função é informar se ainda há capacidade de realização nesse dia. 
    (Garantimos que não ultrapassamos o limite diário.)
    """
    contador = 0

    for exame in exames:
        tipo = exame.get("tipo", "")
        data_marcada = exame.get("data_marcada", "")
        num = exame.get("num", None)

        if tipo == tipo_exame and data_marcada == data_marcada_str:
            if ignorar_num is not None:
                try:
                    if int(num) != int(ignorar_num):
                        contador = contador + 1
                except (TypeError, ValueError):
                    contador = contador + 1
            else:
                contador = contador + 1

    return contador

def primeira_marcacao_livre(exames, tipo_exame: str, inicio: date, ignorar_num=None):
    """
    Motor de agendamento: percorre a funcão e procura o primeiro dia e hora disponível para o 'tipo_exame',
    usando as HORAS_POR_TIPO como slots fixos.
    Se todas as horas desse tipo estiverem cheias NAQUELE dia, avança para o dia seguinte.
    Também respeita o limite diário de CAPACIDADE_DIARIA, se estiver definido.
    """
    limite_diario = int(CAPACIDADE_DIARIA.get(tipo_exame, len(horas_para_tipo(tipo_exame))))
    horas = horas_para_tipo(tipo_exame)

    dia = inicio
    while True:
        data_str = dia.strftime(FORMATO_DATA)

        ocupados_dia = contar_marcados(exames, tipo_exame, data_str, ignorar_num)
        if ocupados_dia < limite_diario:
            for h in horas:
                if not slot_ocupado(exames, tipo_exame, data_str, h, ignorar_num):
                    return dia, h

        dia = dia + timedelta(days=1)

def horas_para_tipo(tipo_exame: str):
    """Devolve a lista de horas fixas para um tipo"""
    if tipo_exame in HORAS_POR_TIPO:
        return HORAS_POR_TIPO[tipo_exame]
    
    
def calcular_estado_exame(data_marcada_date):
    """
    Recebe a data marcada (tipo date) e devolve:
    - "Aprovado" e 0 dias se a data é hoje ou anterior.
    - "Pendente" e nº de dias em espera se é futura.
    """
    hoje_date = date.today()

    if data_marcada_date <= hoje_date:
        return "Aprovado", 0
    else:
        diferenca = data_marcada_date - hoje_date
        dias = diferenca.days #Quando subtraímos duas datas, o Python dá-nos um timedelta (usado tbm em cima) que é um intervalo de tempo. Usamos .days para ficar só com o número de dias,
        return "Pendente", dias


def replanear_pendentes_por_tipo(exames, tipo_exame):
    """
    Reorganiza exames FUTUROS de um determinado tipo, a partir do dia_inicial_marcacao(),
    para que ocupem (data, hora) o mais cedo possível, respeitando:
    - horas fixas por tipo (HORAS_POR_TIPO)
    - limite diário de CAPACIDADE_DIARIA
    Não mexe em exames de datas anteriores ao dia inicial.
    """
    base_date = dia_inicial_marcacao()

    # 1. Selecionar exames deste tipo com data >= base_date
    exames_tipo = []  #criar lista vazia e percorre todos os exames
    for exame in exames: 
        tipo = exame.get("tipo", "")
        if tipo == tipo_exame:
            data_str = exame.get("data_marcada", data_hoje())
            try:
                data = datetime.strptime(data_str, FORMATO_DATA).date()
            except ValueError:
                data = base_date

            if data >= base_date:
                exames_tipo.append(exame) #adicionamos o exame à lista

    # 2. Ordenar por número (ordem previsível) 
    n = len(exames_tipo)   
    for i in range(n - 1):  #numa lista vamos percorrer os exames e verificar o número do exame em questão (i)
        for j in range(i + 1, n):  #de seguida vamos percorrer os exames e ver qual é o número do exame a seguir ao i (j)
            num_i = int(exames_tipo[i].get("num", 0))
            num_j = int(exames_tipo[j].get("num", 0))
            if num_j < num_i:   #se j for menor que i (tipo j= 2 e i= 3), então trocamos a ordem 
                temp = exames_tipo[i]
                exames_tipo[i] = exames_tipo[j]
                exames_tipo[j] = temp

    # 3. Para cada exame, voltar a marcar dia+hora com base nas vagas disponíveis
    for exame in exames_tipo: #vagas libertas, reorganizar
        num = exame.get("num")
        dia, hora = primeira_marcacao_livre(exames, tipo_exame, base_date, ignorar_num=num)
        estado, dias_espera = calcular_estado_exame(dia)

        exame["data_marcada"] = dia.strftime(FORMATO_DATA)
        exame["hora_marcada"] = hora
        exame["resultado"] = estado
        exame["dias_espera"] = dias_espera

def slot_ocupado(exames, tipo_exame: str, data_str: str, hora_str: str, ignorar_num=None) -> bool:
    """
    Retorna True se já há um exame do mesmo tipo no mesmo slot (data+hora).
    """
    for e in exames: #vai percorrer a lista de exames que temos e com o e.get (semelhante ao exame[0], por exemplo) vamos buscar o tipo
        if e.get("tipo") == tipo_exame and e.get("data_marcada") == data_str and e.get("hora_marcada") == hora_str: #a data e a hora disponivel
            if ignorar_num is not None:
                try:
                    if int(e.get("num", -1)) == int(ignorar_num):
                        continue   #o ignorar_num começa com none (não existente) 
                except (TypeError, ValueError): #e quando abrimos um exame para editar este parâmetro assume esse número, ignorando-o 
                    pass  #porque estamos apenas a editar algum parâmetro do exame, não a mudar o número dele
            return True
    return False

# =================== CLASSE PRINCIPAL ===================

class GestorExames(tk.Tk): 
    def __init__(self):
        super().__init__()

        self.title("Gestor de Exames Clínicos")
        self.geometry("1080x620")
        self.configure(bg=BG)

        self.configurar_estilos()

        self.exames = ler_dados()

        self.var_num = tk.StringVar()
        self.var_paciente = tk.StringVar()
        self.var_utente = tk.StringVar()
        self.var_nascimento = tk.StringVar()
        self.var_tipo = tk.StringVar(value=TIPOS_EXAME[0])
        self.var_registo = tk.StringVar(value=data_hoje())
        self.var_busca = tk.StringVar()

        # entrada de pesquisa vai ser guardada aqui depois
        self.entrada_pesquisa = None

        self.criar_interface()
        self.atualizar_tabela()

    def configurar_estilos(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT_DARK)
        style.configure("TLabelframe", background=BG, foreground=TEXT_DARK)
        style.configure("TLabelframe.Label", background=BG, foreground=TEXT_DARK)

        style.configure("Top.TFrame", background=TOP)
        style.configure(
            "Top.TLabel",
            background=TOP,
            foreground="white",
            font=("Segoe UI", 16, "bold")
        )

        style.configure(
            "TButton",
            background=ACCENT,
            foreground=TEXT_DARK,
            padding=6,
            borderwidth=0
        )
        style.map(
            "TButton",
            background=[("active", "#88c9aa"), ("pressed", "#76b898")]
        )

        style.configure(
            "Treeview",
            background="white",
            fieldbackground="white",
            foreground=TEXT_DARK,
            rowheight=22,
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            background=ACCENT,
            foreground=TEXT_DARK,
            font=("Segoe UI", 9, "bold")
        )
        style.map(
            "Treeview.Heading",
            background=[("active", "#88c9aa")]
        )

    # ---------- INTERFACE ----------

    def criar_interface(self):
        topo = ttk.Frame(self, style="Top.TFrame")
        topo.pack(fill=tk.X)

        ttk.Label(
            topo,
            text="🩺 Gestor de Exames Clínicos",
            style="Top.TLabel"
        ).pack(side=tk.LEFT, padx=10, pady=8)

        ttk.Button(
            topo,
            text="💾 Guardar ficheiro",
            command=self.botao_gravar_ficheiro
        ).pack(side=tk.RIGHT, padx=5, pady=8)

        ttk.Button(
            topo,
            text="↻ Recarregar ficheiro",
            command=self.recarregar
        ).pack(side=tk.RIGHT, padx=5, pady=8)

        form = ttk.LabelFrame(self, text="Novo / Editar Exame", padding=10)
        form.pack(fill=tk.X, padx=10, pady=(8, 8))

        ttk.Label(form, text="Nº Exame:").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.var_num, width=10, state="readonly").grid(row=0, column=1, padx=3)

        ttk.Label(form, text="Nome do Paciente:").grid(row=0, column=2, sticky="w")
        ttk.Entry(form, textvariable=self.var_paciente, width=30).grid(row=0, column=3, padx=3)

        ttk.Label(form, text="Nº Utente:").grid(row=0, column=4, sticky="w")
        ttk.Entry(form, textvariable=self.var_utente, width=18).grid(row=0, column=5, padx=3)

        ttk.Label(form, text="Data de Nascimento (dd-mm-yyyy):").grid(row=1, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.var_nascimento, width=18).grid(row=1, column=1, padx=3)

        ttk.Label(form, text="Tipo de Exame:").grid(row=1, column=2, sticky="w")
        ttk.Combobox(
            form,
            textvariable=self.var_tipo,
            values=TIPOS_EXAME,
            state="readonly",
            width=27
        ).grid(row=1, column=3, padx=3)

        ttk.Label(form, text="Data de Registo:").grid(row=1, column=4, sticky="w")
        ttk.Entry(form, textvariable=self.var_registo, width=18, state="readonly").grid(row=1, column=5, padx=3)

        botoes = ttk.Frame(form)
        botoes.grid(row=0, column=6, rowspan=2, padx=10)

        ttk.Button(botoes, text="🆕 Novo", command=self.novo_exame).pack(fill=tk.X, pady=2)
        ttk.Button(botoes, text="✅ Guardar", command=self.guardar_exame).pack(fill=tk.X, pady=2)
        ttk.Button(botoes, text="🗑️ Apagar", command=self.apagar_exame).pack(fill=tk.X, pady=2)
        ttk.Button(botoes, text="🧹 Limpar", command=self.limpar_formulario).pack(fill=tk.X, pady=2)

        frame_pesquisa = ttk.LabelFrame(
            self,
            text="Pesquisa (Nome, Tipo, Nº Utente ou Estado)",
            padding=8
        )
        frame_pesquisa.pack(fill=tk.X, padx=10, pady=(0, 8))

        ttk.Label(frame_pesquisa, text="Termo de pesquisa:").pack(side=tk.LEFT)

        # Guardamos a entrada de pesquisa em self.entrada_pesquisa
        self.entrada_pesquisa = ttk.Entry(frame_pesquisa, textvariable=self.var_busca, width=40)
        self.entrada_pesquisa.pack(side=tk.LEFT, padx=5)
        self.entrada_pesquisa.bind("<Return>", self._enter_pesquisa)

        ttk.Button(frame_pesquisa, text="🔍 Procurar", command=self.atualizar_tabela).pack(side=tk.LEFT, padx=3)
        ttk.Button(frame_pesquisa, text="Limpar filtro", command=self.limpar_filtro).pack(side=tk.LEFT, padx=3)
        ttk.Button(frame_pesquisa, text="Exportar CSV", command=self.exportar_csv).pack(side=tk.RIGHT)

        frame_tabela = ttk.Frame(self)
        frame_tabela.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        colunas = (
            "num", "paciente", "utente", "nascimento",
            "tipo", "data_registo", "data_marcada", "hora_marcada",
            "dias_espera", "resultado"
        )

        self.tabela = ttk.Treeview(
            frame_tabela,
            columns=colunas,
            show="headings",
            height=15,
            selectmode="extended"
        )

        self.tabela.heading("num", text="Nº")
        self.tabela.heading("paciente", text="Paciente")
        self.tabela.heading("utente", text="Utente")
        self.tabela.heading("nascimento", text="Nascimento")
        self.tabela.heading("tipo", text="Tipo de Exame")
        self.tabela.heading("data_registo", text="Registo")
        self.tabela.heading("data_marcada", text="Data")
        self.tabela.heading("hora_marcada", text="Hora")
        self.tabela.heading("dias_espera", text="Espera (dias)")
        self.tabela.heading("resultado", text="Estado")

        self.tabela.column("num", width=60, anchor="center")
        self.tabela.column("paciente", width=220, anchor="w")
        self.tabela.column("utente", width=120, anchor="center")
        self.tabela.column("nascimento", width=110, anchor="center")
        self.tabela.column("tipo", width=150, anchor="w")
        self.tabela.column("data_registo", width=110, anchor="center")
        self.tabela.column("data_marcada", width=90, anchor="center")
        self.tabela.column("hora_marcada", width=70, anchor="center")
        self.tabela.column("dias_espera", width=90, anchor="center")
        self.tabela.column("resultado", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=scrollbar.set)

        self.tabela.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tabela.bind("<<TreeviewSelect>>", self.carregar_selecao)
        # Duplo clique abre janela de detalhes
        self.tabela.bind("<Double-1>", self.abrir_detalhes_exame)

        self.label_status = ttk.Label(self, text="", padding=8)
        self.label_status.pack(fill=tk.X, side=tk.BOTTOM)

        # ---------- ATALHOS DE TECLADO ----------
        # Enter (fora da caixa de pesquisa) -> guardar exame
        self.bind("<Return>", self._atalho_enter)

        # Ctrl+N -> novo exame
        self.bind("<Control-n>", self._atalho_novo)

        # Ctrl+S -> guardar exame
        self.bind("<Control-s>", self._atalho_guardar)

        # Delete -> apagar exame selecionado / atual
        self.bind("<Delete>", self._atalho_apagar)

    # ---------- HANDLERS SIMPLES / ATALHOS ----------

    def _enter_pesquisa(self, event):
        """Enter na caixa de pesquisa atualiza a tabela e não deixa o Enter global interferir."""
        self.atualizar_tabela()
        return "break"

    def _atalho_enter(self, event):
        """
        Atalho global para Enter:
        - Se o foco estiver na caixa de pesquisa, deixamos o _enter_pesquisa tratar.
        - Caso contrário, usamos Enter para guardar o exame.
        """
        widget_foco = self.focus_get()
        if widget_foco is self.entrada_pesquisa:
            # já tratado no _enter_pesquisa
            return

        self.guardar_exame()
        return "break"

    def _atalho_novo(self, event):
        """Ctrl+N -> Novo exame"""
        self.novo_exame()
        return "break"

    def _atalho_guardar(self, event):
        """Ctrl+S -> Guardar exame"""
        self.guardar_exame()
        return "break"

    def _atalho_apagar(self, event):
        """Delete -> Apagar exame"""
        self.apagar_exame()
        return "break"

    # ---------- LÓGICA PRINCIPAL ----------

    def atualizar_tabela(self):
    # 1) Atualizar estado e dias_espera de todos os exames em função da data marcada
       for exame in self.exames: #vamos buscar o ficheiro onde temos os exames e percorremos o dicionario, a lista
        data_str = exame.get("data_marcada", "") #e vamos buscar a data em formato string
        if not data_str:
            continue

        try:
            data_marcada_date = datetime.strptime(data_str, FORMATO_DATA).date()
        except ValueError:
            # Se a data estiver mal formatada ou não estiver marcada, ignoramos este exame
            continue

        estado, dias_espera = calcular_estado_exame(data_marcada_date) #vamos chamar a função auxiliar que
        exame["resultado"] = estado                                   # decide se o estado é aprovado ou pendente
        exame["dias_espera"] = dias_espera

        termo = self.var_busca.get().strip().lower()   #lemos o que esta escrito na caixa de pesquisa
                                                       #configuramos e tiramos o espaço e pomos tudo em miniscula para facilitar comparação
        if termo == "":           #se tiver vazio, não ha filtro, mostramos todos os exames
            exames_a_mostrar = self.exames
        else:
            exames_a_mostrar = []                         #se houver, criamos uma lista vazia
            for exame in self.exames:                      # e para cada exame vamos buscar este parametros
                nome = exame.get("paciente", "").lower()
                tipo = exame.get("tipo", "").lower()
                utente = exame.get("utente", "").lower()
                estado = exame.get("resultado", "").lower()

                if (termo in nome
                        or termo in tipo
                        or termo in utente
                        or termo in estado):
                    exames_a_mostrar.append(exame) #se o termo estiver presente, adicionamos à lista, se não, não filtra

        def chave_ordem(exame):
            data_marcada = exame.get("data_marcada", data_hoje())
            hora_marcada = exame.get("hora_marcada", "00:00")
            return (data_marcada, hora_marcada) #esta função devolve um par (data e hora)

        tamanho = len(exames_a_mostrar)
        for i in range(tamanho - 1):
            for j in range(i + 1, tamanho):
                if chave_ordem(exames_a_mostrar[j]) < chave_ordem(exames_a_mostrar[i]):
                    temp = exames_a_mostrar[i]
                    exames_a_mostrar[i] = exames_a_mostrar[j]
                    exames_a_mostrar[j] = temp    #vai seguir a mesma lógica que a função replanear pendentes e organiza por ordem cronologica

        for item in self.tabela.get_children():
            self.tabela.delete(item)

        for exame in exames_a_mostrar:
            valores = (
                exame.get("num", ""),
                exame.get("paciente", ""),
                exame.get("utente", ""),
                exame.get("nascimento", ""),
                exame.get("tipo", ""),
                exame.get("data_registo", ""),
                exame.get("data_marcada", ""),
                exame.get("hora_marcada", ""),
                exame.get("dias_espera", ""),
                exame.get("resultado", "")
            )
            self.tabela.insert("", tk.END, iid=str(exame.get("num", "")), values=valores)

        total = len(self.exames)
        pendentes = 0
        aprovados = 0
        for exame in self.exames:
            estado = exame.get("resultado", "")
            if estado == "Pendente":
                pendentes = pendentes + 1
            elif estado == "Aprovado":
                aprovados = aprovados + 1                 #resumidamente atualizamos o rodapé e a aplicação 

        self.label_status.config(
            text=f"Total de exames: {total} | Aprovados: {aprovados} | Pendentes: {pendentes}"
        )

    def limpar_filtro(self): #apaga a pesquisa e atualiza a tabela
        self.var_busca.set("")
        self.atualizar_tabela()

    def novo_exame(self): #prepara um novo registo e limpa o formulário
        self.limpar_formulario()
        proximo = proximo_numero(self.exames)
        self.var_num.set(str(proximo))

    def limpar_formulario(self): #limpa todos os campos de entrada de dados
        self.var_num.set("")
        self.var_paciente.set("")
        self.var_utente.set("")
        self.var_nascimento.set("")
        self.var_tipo.set(TIPOS_EXAME[0])
        self.var_registo.set(data_hoje())

    def guardar_exame(self):
        """controlador principal, verifica se o número de exame existe
        Guarda um novo exame ou atualiza um existente (com data+hora fixas por tipo)."""
        nome = self.var_paciente.get().strip()
        utente = self.var_utente.get().strip()
        nascimento = self.var_nascimento.get().strip()
        tipo = self.var_tipo.get().strip()
        data_registo = self.var_registo.get().strip()
        num_str = self.var_num.get().strip()

        if nome == "":
            messagebox.showerror("Erro", "Indique o nome do paciente.")
            return

        if not validar_utente(utente):
            messagebox.showerror("Erro", "Nº de utente inválido. Deve ter 9 a 11 dígitos.")
            return

        if not validar_data(nascimento):
            messagebox.showerror("Erro", "Data de nascimento inválida. Use o formato dd-mm-yyyy.")
            return

        inicio_marcacao = dia_inicial_marcacao()

        exame_existente = None
        if num_str != "":
            for exame in self.exames:
                if str(exame.get("num")) == num_str:
                    exame_existente = exame
                    break

        if exame_existente is not None:
            numero = exame_existente.get("num")
            tipo_antigo = exame_existente.get("tipo", "")

            dia, hora = primeira_marcacao_livre(self.exames, tipo, inicio_marcacao, ignorar_num=numero)
            estado, dias_espera = calcular_estado_exame(dia)
            data_marcada_str = dia.strftime(FORMATO_DATA)

            exame_existente["paciente"] = nome
            exame_existente["utente"] = utente
            exame_existente["nascimento"] = nascimento
            exame_existente["tipo"] = tipo
            exame_existente["data_registo"] = data_registo
            exame_existente["data_marcada"] = data_marcada_str
            exame_existente["hora_marcada"] = hora
            exame_existente["resultado"] = estado
            exame_existente["dias_espera"] = dias_espera

            if tipo_antigo != "" and tipo_antigo != tipo:
                replanear_pendentes_por_tipo(self.exames, tipo_antigo)

            replanear_pendentes_por_tipo(self.exames, tipo)

            gravar_dados(self.exames)
            self.atualizar_tabela()
            messagebox.showinfo("Atualizado", f"Exame #{numero} atualizado com sucesso.")
        else:
            if num_str == "":
                numero = proximo_numero(self.exames)
            else:
                numero = int(num_str)

            dia, hora = primeira_marcacao_livre(self.exames, tipo, inicio_marcacao)
            estado, dias_espera = calcular_estado_exame(dia)
            data_marcada_str = dia.strftime(FORMATO_DATA)

            novo_exame = {
                "num": numero,
                "paciente": nome,
                "utente": utente,
                "nascimento": nascimento,
                "tipo": tipo,
                "data_registo": data_registo,
                "data_marcada": data_marcada_str,
                "hora_marcada": hora,
                "resultado": estado,
                "dias_espera": dias_espera
            }

            self.exames.append(novo_exame)

            replanear_pendentes_por_tipo(self.exames, tipo)

            gravar_dados(self.exames)
            self.var_num.set(str(numero))
            self.atualizar_tabela()
            messagebox.showinfo("Guardado", f"Exame #{numero} registado com sucesso.")

    def apagar_exame(self): #se existirem linhas selecionadas
        selecionados = self.tabela.selection() #vamos buscar a função que nos permite selecionar itens 

        if selecionados: #se selecionarmos
            numeros_para_apagar = [] #recolhe uma lista dos exames 
            tipos_afetados = []  # e dos tipos de exame

            for iid in selecionados:
                num_str = str(iid)    #por cada elemento dos selecionados nos vamos converter numa sring e vamos buscar ao ficheiro
                for exame in self.exames:
                    if str(exame.get("num")) == num_str:
                        numeros_para_apagar.append(num_str)
                        tipos_afetados.append(exame.get("tipo", ""))
                        break

            if len(numeros_para_apagar) == 0: 
                messagebox.showerror("Erro", "Não foi possível encontrar os exames selecionados.")
                return

            texto_lista = ", ".join(numeros_para_apagar)

            confirmar = messagebox.askyesno(
                "Confirmar",
                f"Tem a certeza que pretende apagar os exames #{texto_lista}?"
            )

            if confirmar:
                nova_lista = []
                for exame in self.exames:
                    num_atual = str(exame.get("num", ""))
                    if num_atual not in numeros_para_apagar:
                        nova_lista.append(exame)

                self.exames = nova_lista

                tipos_unicos = []
                for t in tipos_afetados:
                    if t != "" and t not in tipos_unicos:
                        tipos_unicos.append(t)

                for t in tipos_unicos:
                    replanear_pendentes_por_tipo(self.exames, t)

                gravar_dados(self.exames)
                self.limpar_formulario()
                self.atualizar_tabela()
                messagebox.showinfo("Removido", f"Exames #{texto_lista} removidos.")
            return

        num_str = self.var_num.get().strip()

        if num_str == "":
            messagebox.showwarning("Aviso", "Selecione um exame na tabela ou no formulário para apagar.")
            return

        exame_a_apagar = None
        for exame in self.exames:
            if str(exame.get("num")) == num_str:
                exame_a_apagar = exame
                break

        if exame_a_apagar is None:
            messagebox.showerror("Erro", "Exame não encontrado.")
            return

        confirmar = messagebox.askyesno(
            "Confirmar",
            f"Tem a certeza que pretende apagar o exame #{num_str}?"
        )

        if confirmar:
            tipo_removido = exame_a_apagar.get("tipo", "")
            self.exames.remove(exame_a_apagar)

            if tipo_removido != "":
                replanear_pendentes_por_tipo(self.exames, tipo_removido)

            gravar_dados(self.exames)
            self.limpar_formulario()
            self.atualizar_tabela()
            messagebox.showinfo("Removido", f"Exame #{num_str} removido.")

    def carregar_selecao(self, event):
        selecionados = self.tabela.selection()

        if not selecionados:
            return

        iid = selecionados[0]
        num_selecionado = str(iid)

        for exame in self.exames:
            if str(exame.get("num")) == num_selecionado:
                self.var_num.set(str(exame.get("num", "")))
                self.var_paciente.set(exame.get("paciente", ""))
                self.var_utente.set(exame.get("utente", ""))
                self.var_nascimento.set(exame.get("nascimento", ""))
                self.var_tipo.set(exame.get("tipo", TIPOS_EXAME[0]))
                self.var_registo.set(exame.get("data_registo", data_hoje()))
                break
    def abrir_detalhes_exame(self, event):
        """
        Abre uma janela com os detalhes do exame selecionado
        quando o utilizador faz duplo-clique numa linha da tabela.
        """
        selecionados = self.tabela.selection()
        if not selecionados:
            return

        iid = selecionados[0]
        num_selecionado = str(iid)

        exame_encontrado = None
        for exame in self.exames:
            if str(exame.get("num")) == num_selecionado:
                exame_encontrado = exame
                break

        if exame_encontrado is None:
            return

        janela = tk.Toplevel(self)
        janela.title(f"Detalhes do exame #{num_selecionado}")
        janela.transient(self)
        janela.grab_set()
        janela.resizable(False, False)

        campos = [
            ("Nº Exame", exame_encontrado.get("num", "")),
            ("Nome do Paciente", exame_encontrado.get("paciente", "")),
            ("Nº Utente", exame_encontrado.get("utente", "")),
            ("Data de Nascimento", exame_encontrado.get("nascimento", "")),
            ("Tipo de Exame", exame_encontrado.get("tipo", "")),
            ("Data de Registo", exame_encontrado.get("data_registo", "")),
            ("Data Marcada", exame_encontrado.get("data_marcada", "")),
            ("Hora Marcada", exame_encontrado.get("hora_marcada", "")),
            ("Dias de Espera", exame_encontrado.get("dias_espera", "")),
            ("Estado", exame_encontrado.get("resultado", "")),
        ]

        frame = ttk.Frame(janela, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        for i, (rotulo, valor) in enumerate(campos):
            ttk.Label(frame, text=f"{rotulo}:").grid(
                row=i, column=0, sticky="w", pady=2, padx=(0, 8)
            )
            ttk.Label(frame, text=str(valor)).grid(
                row=i, column=1, sticky="w", pady=2
            )

        ttk.Button(frame, text="Fechar", command=janela.destroy).grid(
            row=len(campos), column=0, columnspan=2, pady=(10, 0)
        )

    def recarregar(self):
        self.exames = ler_dados()
        self.atualizar_tabela()
        messagebox.showinfo("Recarregado", "Dados recarregados a partir do ficheiro.")

    def exportar_csv(self):
        if len(self.exames) == 0:
            messagebox.showinfo("Exportar CSV", "Não há dados para exportar.")
            return

        caminho = filedialog.asksaveasfilename(
            title="Exportar para CSV",
            defaultextension=".csv",
            filetypes=[("Ficheiros CSV", "*.csv")]
        )

        if not caminho:
            return

        try:
            exames_ordenados = list(self.exames)
            n = len(exames_ordenados)
            for i in range(n - 1):
                for j in range(i + 1, n):
                    num_i = int(exames_ordenados[i].get("num", 0))
                    num_j = int(exames_ordenados[j].get("num", 0))
                    if num_j < num_i:
                        temp = exames_ordenados[i]
                        exames_ordenados[i] = exames_ordenados[j]
                        exames_ordenados[j] = temp

            with open(caminho, "w", newline="", encoding="utf-8") as f:
                escritor = csv.writer(f, delimiter=";")
                escritor.writerow([
                    "num", "paciente", "utente", "nascimento", "tipo",
                    "data_registo", "data_marcada", "hora_marcada",
                    "dias_espera", "resultado"
                ])

                for exame in exames_ordenados:
                    linha = [
                        exame.get("num", ""),
                        exame.get("paciente", ""),
                        exame.get("utente", ""),
                        exame.get("nascimento", ""),
                        exame.get("tipo", ""),
                        exame.get("data_registo", ""),
                        exame.get("data_marcada", ""),
                        exame.get("hora_marcada", ""),
                        exame.get("dias_espera", ""),
                        exame.get("resultado", "")
                    ]
                    escritor.writerow(linha)

            messagebox.showinfo("Exportar CSV", "Exportação concluída com sucesso.")
        except OSError as e:
            messagebox.showerror("Erro", f"Erro ao exportar CSV: {e}")

    def botao_gravar_ficheiro(self):
        sucesso = gravar_dados(self.exames)
        if sucesso:
            messagebox.showinfo("Gravar", "Dados gravados com sucesso.")

# =================== EXECUTAR ===================

if __name__ == "__main__":
    app = GestorExames()
    app.mainloop()


# Recursos, referências e inspirações consultados durante o desenvolvimento da aplicação:
#   
# - https://github.com/WildLeoKnight/Hospital-Schedule-App.git
# - https://github.com/Alibro005/Hospital-Management-System.git
# - https://github.com/Python-mini-project/Hospital-Schedule-Management-System.git
#
# Tutoriais de apoio (Python, Tkinter, JSON, etc.):
#   
# - https://www.youtube.com/watch?v=St48epdRDZw&t=332s
# - https://www.youtube.com/watch?v=Ro_MScTDfU4
# - https://www.youtube.com/watch?v=0ZaC6JaNpic (e as respetivas partes seguintes)
# - https://www.youtube.com/watch?v=a5iCRrygWxk&t=629s
# - https://www.youtube.com/watch?v=RQOXVpaFYMU
# - https://www.youtube.com/watch?v=ZDa-Z5JzLYM (e as respetivas partes seguintes)
# - https://www.youtube.com/watch?v=vB6hfWRX1ds
# - https://www.youtube.com/watch?v=JUGEkFDeuwg (e as respetivas partes seguintes)
# - https://www.youtube.com/watch?v=f_9NBdSAo-g
#
# Ferramentas de apoio para esclarecer dúvidas e rever código:
#
# - figma: para criação do rascunho de como poderia vir a ser a aplicação
# - chatgtp 
# - blackbox.ai 
