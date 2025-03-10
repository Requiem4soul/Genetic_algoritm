from algorithm.generation import Generation
from algorithm.network import Network

def main():
    # Параметры алгоритма
    size = 20  # Размер графа
    k = 1      # Коэффициент для расчёта population_size
    start = None
    end = None
    min_population = 10  # Минимальное количество хромосом
    max_population = 100  # Максимальное количество хромосом
    max_generations = 200  # Максимальное количество поколений
    mutation_probability = 0.5  # Вероятность мутации

    # Создаём сеть
    network = Network(size=size, start=start, end=end)

    # Выводим граф (матрицу смежности)
    print("Граф:")
    network.print_graph_with_vertices()

    # Выводим оптимальное решение по Флойду
    network.print_optimal_solution()

    # Создаём начальное поколение
    generation = Generation(network, k=k, min_population=min_population, max_population=max_population)

    # Основной цикл генетического алгоритма
    for gen in range(max_generations):
        generation.evolve(gen + 1, mutation_probability)

        # Лучшая хромосома в текущем поколении
        best_chromosome = generation.get_best_chromosome()

        # Статистика популяции
        stats = generation.get_population_stats()
        print(f"\nСтатистика по поколению {gen + 1}:")
        print(f"  Лучший фитнес: {stats['best_fitness']} ({stats['best_percent']} от оптимального)")
        print(f"  Худший фитнес: {stats['worst_fitness']} ({stats['worst_percent']} от оптимального)")
        print(f"  Средний фитнес: {stats['average_fitness']} ({stats['average_percent']} от оптимального)")

    # Возвращаем лучшее решение
    best_solution = generation.get_best_chromosome()

    # Выводим результат
    print("\nЛучшее решение:")
    print(f"Путь: {best_solution.path}")
    print(f"Длина: {best_solution.fitness}")

if __name__ == "__main__":
    main()