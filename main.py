import math
import tkinter as tk
from tkinter import messagebox

NUM_BUCKETS = 0
BUCKET_LIMIT = 0
PAGE_SIZE = 0  # Tamanho das páginas, definido pelo usuário
NUM_PAGES = 0
FR = 2  # Número máximo de tuplas endereçadas por bucket

total_collisions = 0
total_overflows = 0

hash_table = []
pages = []


def hash_function(word: str):
    LARGE_PRIME_NUMBER = 65521

    checksum = 0

    for i in range(len(word)):
        checksum *= LARGE_PRIME_NUMBER
        checksum += ord(word[i].lower())
    return checksum % NUM_BUCKETS


def add_to_bucket(index, info_tuple):
    global total_collisions, total_overflows
    bucket = hash_table[index]

    # Colisão: ocorre quando é adicionada uma tupla a um bucket não vazio
    if len(bucket) > 0:
        total_collisions += 1

    # Overflow: Ocorre quando é adicionado uma tupla a um bucket não vazio
    if len(bucket) >= BUCKET_LIMIT:
        total_overflows += 1

    bucket.append(info_tuple)


def load_words(file_path):
    global hash_table, NUM_BUCKETS, NUM_PAGES, PAGE_SIZE, BUCKET_LIMIT, total_collisions, total_overflows, pages
    words = []

    try:
        # Read words from file
        with open(file_path, "r") as file:
            words = [line.strip() for line in file]

        NUM_PAGES = (len(words) + PAGE_SIZE - 1) // PAGE_SIZE

        pages = [[] for _ in range(NUM_PAGES)]

        # Populate pages
        page_index = 0
        for word in words:
            if len(pages[page_index]) >= PAGE_SIZE:
                page_index += 1
            pages[page_index].append(word)

        # Calculate number of buckets
        NUM_BUCKETS = math.ceil(len(words))
        hash_table = [[] for _ in range(NUM_BUCKETS)]
        BUCKET_LIMIT = FR

        # Metrics counters
        total_collisions = 0
        total_overflows = 0

        # Populate buckets
        for page_number, page in enumerate(pages):
            for word in page:
                index = hash_function(word)
                add_to_bucket(index, (word, page_number))

        messagebox.showinfo(
            "Carregamento",
            f"Palavras carregadas com sucesso!\nNúmero de páginas: {NUM_PAGES}\nNúmero de buckets: {NUM_BUCKETS}",
        )
    except FileNotFoundError:
        messagebox.showerror("Erro", f"Arquivo {file_path} não encontrado.")


def search_word():
    wanted_word = search_entry.get().strip()
    index = hash_function(wanted_word)
    bucket = hash_table[index]
    cost = 0

    while bucket:
        cost += 1

        for entry in bucket:
            if isinstance(entry, list):
                continue

            if entry[0] == wanted_word:
                page = entry[1]
                messagebox.showinfo(
                    "Resultado da Busca",
                    f"Palavra '{wanted_word}' encontrada.\nCusto da busca: {cost} leituras.\nNúmero da página: {page}",
                )
                return

        if isinstance(bucket[-1], list):
            bucket = bucket[-1]

        else:
            break

    messagebox.showinfo(
        "Resultado da Busca",
        f"Palavra '{wanted_word}' não encontrada.\nCusto da busca: {cost} leituras.",
    )


def table_scan():
    word = search_entry.get().strip()
    found = False
    scan_page = 0
    scan_cost = 0
    global pages


    for index, page in enumerate(pages):
        scan_cost += 1

        if word in page:
            found = True
            scan_page = index + 1
            break


    if found:
        messagebox.showinfo(
            "Resultado da Busca",
            f"Palavra '{word}' encontrada.\nCusto da busca: {scan_cost} leituras.\nNúmero da página: {scan_page}",
        )

    else:
        messagebox.showinfo(
            "Resultado da Busca",
            f"Palavra '{word}' não encontrada.\nCusto da busca: {scan_cost} leituras.",
        )


def initialize_load():
    global PAGE_SIZE
    try:
        PAGE_SIZE = int(page_size_entry.get())
        if PAGE_SIZE <= 0:
            raise ValueError("O tamanho da página deve ser maior que zero.")
        load_words("words.txt")
        collision_rate = (
            (total_collisions / len(hash_table)) * 100 if len(hash_table) > 0 else 0
        )
        overflow_rate = (
            (total_overflows / len(hash_table)) * 100 if len(hash_table) > 0 else 0
        )
        messagebox.showinfo(
            "Estatísticas",
            f"Taxa de colisões: {collision_rate:.2f}%\nTaxa de overflows: {overflow_rate:.2f}%",
        )
    except ValueError as e:
        messagebox.showerror("Erro", str(e))


root = tk.Tk()
root.title("Busca de Palavras com Índice Hash e Table Scan")

frame = tk.Frame(root)
frame.pack(pady=20)

page_size_label = tk.Label(frame, text="Tamanho da Página:")
page_size_label.pack(side=tk.LEFT, padx=5)

page_size_entry = tk.Entry(frame, width=10)
page_size_entry.pack(side=tk.LEFT, padx=5)

load_button = tk.Button(frame, text="Carregar Palavras", command=initialize_load)
load_button.pack(side=tk.LEFT, padx=5)

search_entry = tk.Entry(frame, width=30)
search_entry.pack(side=tk.LEFT, padx=5)

label = tk.Label(frame, text="Digite a palavra para buscar:")
label.pack(side=tk.LEFT, padx=5)

search_button = tk.Button(frame, text="Buscar", command=search_word)
search_button.pack(side=tk.LEFT, padx=5)

scan_button = tk.Button(frame, text="Table Scan", command=table_scan)
scan_button.pack(side=tk.LEFT, padx=5)

root.mainloop()
