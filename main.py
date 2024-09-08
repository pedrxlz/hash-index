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


def add_to_bucket(index, page):
    global total_collisions, total_overflows
    bucket = hash_table[index]

    if len(bucket) > 0:
        total_collisions += 1

    while len(bucket) >= BUCKET_LIMIT:
        if isinstance(bucket[-1], list):
            bucket = bucket[-1]
        else:
            new_bucket = []
            bucket.append(new_bucket)
            bucket = new_bucket
            total_overflows += 1  # Incrementa o contador de overflows

    bucket.append(page)


def load_words(file_path):
    global hash_table, NUM_BUCKETS, NUM_PAGES, PAGE_SIZE, BUCKET_LIMIT, total_collisions, total_overflows
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
    scan_result = []
    scan_cost = 0

    for bucket_index, bucket in enumerate(hash_table):
        current_bucket = bucket
        while current_bucket:
            scan_cost += 1
            for entry_index, entry in enumerate(current_bucket):
                if isinstance(entry, list):
                    continue

                if entry[0] == word:
                    found = True
                    scan_result.append(
                        f"Palavra '{word}' encontrada\nPágina: {entry[1]}."
                    )
                    break
            if found:
                break
            if isinstance(current_bucket[-1], list):
                current_bucket = current_bucket[-1]
            else:
                break

    if found:
        messagebox.showinfo(
            "Table Scan",
            f"Palavra '{word}' encontrada após {scan_cost} leituras.\n\n"
            + "\n".join(scan_result),
        )
    else:
        messagebox.showinfo(
            "Table Scan",
            f"Palavra '{word}' não encontrada após {scan_cost} leituras.\n\n"
            + "\n".join(scan_result),
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
