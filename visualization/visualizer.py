import sys
import matplotlib.pyplot as plt
import networkx as nx
import tkinter as tk
from tkinter import ttk


def plot_fitness(history):
    """Отрисовка графика фитнеса по поколениям."""
    best_fitness = [float(h["stats"]["best_fitness"]) if h["stats"]["best_fitness"] != "-" else float("inf") for h in
                    history]
    worst_fitness = [float(h["stats"]["worst_fitness"]) if h["stats"]["worst_fitness"] != "-" else float("inf") for h in
                     history]
    avg_fitness = [float(h["stats"]["average_fitness"]) if h["stats"]["average_fitness"] != "-" else float("inf") for h
                   in history]

    plt.figure(figsize=(12, 8))
    plt.subplot(2, 1, 1)
    plt.plot(range(1, len(history) + 1), best_fitness, label="Лучший фитнес", color="green")
    plt.plot(range(1, len(history) + 1), avg_fitness, label="Средний фитнес", color="blue")
    plt.plot(range(1, len(history) + 1), worst_fitness, label="Худший фитнес", color="red")
    plt.xlabel("Поколение")
    plt.ylabel("Фитнес")
    plt.legend()
    plt.title("Статистика фитнеса по поколениям")


def draw_network(network):
    """Отрисовка графа сети."""
    plt.subplot(2, 1, 2)
    G = nx.DiGraph()
    for i in range(network.size):
        for j in range(network.size):
            weight = network.get_weight(i, j)
            if weight is not None and weight != 0:
                G.add_edge(i, j, weight=weight)

    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=500, font_size=10, arrows=True)
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.title("Граф сети")


def visualize(network, history):
    """Основная функция визуализации с интерфейсом."""
    root = tk.Tk()
    root.title("Визуализация генетического алгоритма")

    # Функция для форматирования фитнеса
    def format_fitness(fitness):
        return "-" if fitness >= sys.maxsize else f"{fitness}"

    # Отрисовка графиков
    plot_fitness(history)
    draw_network(network)
    plt.tight_layout()
    plt.savefig("overview.png")
    plt.close()

    # Отображение графиков в Tkinter
    overview_img = tk.PhotoImage(file="overview.png")
    overview_label = tk.Label(root, image=overview_img)
    overview_label.pack()

    # Выбор поколения
    tk.Label(root, text="Выберите поколение:").pack()
    gen_var = tk.IntVar(value=1)
    gen_selector = ttk.Combobox(root, textvariable=gen_var, values=list(range(1, len(history) + 1)))
    gen_selector.pack()

    # Текстовое поле для информации
    info_text = tk.Text(root, height=20, width=80)
    info_text.pack()

    def update_info(*args):
        gen = gen_var.get() - 1
        info_text.delete(1.0, tk.END)
        h = history[gen]

        info_text.insert(tk.END, f"Поколение {gen + 1}:\n\n")
        info_text.insert(tk.END, "Кроссовер:\n")
        for c in h["crossover"]:
            info_text.insert(tk.END, f"Родитель 1: {c['parent1'][0]}, фитнес: {format_fitness(c['parent1'][1])}\n")
            info_text.insert(tk.END, f"Родитель 2: {c['parent2'][0]}, фитнес: {format_fitness(c['parent2'][1])}\n")
            info_text.insert(tk.END, f"Линия кроссовера: {c['cross_line']}\n")
            info_text.insert(tk.END, f"Потомок 1: {c['child1'][0]}, фитнес: {format_fitness(c['child1'][1])}\n")
            info_text.insert(tk.END, f"Потомок 2: {c['child2'][0]}, фитнес: {format_fitness(c['child2'][1])}\n\n")

        info_text.insert(tk.END, "Мутации:\n")
        for m in h["mutation"]:
            info_text.insert(tk.END, f"Было: {m['old'][0]}, фитнес: {format_fitness(m['old'][1])}\n")
            info_text.insert(tk.END, f"Стало: {m['new'][0]}, фитнес: {format_fitness(m['new'][1])}\n\n")

        info_text.insert(tk.END, "Финальная популяция:\n")
        for i, (path, fitness) in enumerate(h["population"]):
            info_text.insert(tk.END, f"Хромосома {i + 1}: {path}, фитнес: {format_fitness(fitness)}\n")

    gen_var.trace("w", update_info)
    update_info()  # Начальный вызов

    root.mainloop()