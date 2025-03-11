from algorithm.generation import Generation
from algorithm.network import Network
from visualization.visualizer import visualize
import sys

def main():
    # Параметры алгоритма
    size = 20
    k = 1
    start = None
    end = None
    min_population = 10
    max_population = 100
    max_generations = 200
    mutation_probability = 0.5

    # Создаём сеть
    network = Network(size=size, start=start, end=end)

    # Выводим граф (матрицу смежности)
    print("Граф:")
    network.print_graph_with_vertices()

    # Выводим оптимальное решение по Флойду
    network.print_optimal_solution()

    # Создаём начальное поколение
    generation = Generation(network, k=k, min_population=min_population, max_population=max_population)

    # Список для хранения данных по поколениям
    history = []

    # Перехватываем данные о кроссовере и мутациях
    crossover_data = []
    mutation_data = []

    def capture_crossover(parent1, parent2, child1, child2, cross_line):
        crossover_data.append({
            "parent1": (parent1.path, parent1.fitness),
            "parent2": (parent2.path, parent2.fitness),
            "child1": (child1.path, child1.fitness),
            "child2": (child2.path, child2.fitness),
            "cross_line": cross_line
        })

    def capture_mutation(old_path, old_fitness, new_path, new_fitness):
        mutation_data.append({
            "old": (old_path, old_fitness),
            "new": (new_path, new_fitness)
        })

    # Сохраняем оригинальные методы
    original_evolve = generation.evolve
    original_crossover = generation.perform_crossover

    # Модифицированный кроссовер
    def modified_crossover(pairs):
        result = original_crossover(pairs)
        for parent1, parent2 in pairs:
            child1, child2, cross_line = parent1.crossover(parent2, random_or_not=True)
            capture_crossover(parent1, parent2, child1, child2, cross_line)
        return result

    # Модифицированная эволюция
    def modified_evolve(gen_num, mut_prob):
        # Очищаем данные для нового поколения
        crossover_data.clear()
        mutation_data.clear()
        # Устанавливаем модифицированный кроссовер
        generation.perform_crossover = modified_crossover
        # Выполняем оригинальную эволюцию
        original_evolve(gen_num, mut_prob)
        # Применяем мутации и собираем данные
        for chromosome in generation.population:
            old_path = chromosome.path.copy()
            old_fitness = chromosome.fitness
            chromosome.mutation(mut_prob)
            if chromosome.path != old_path:
                capture_mutation(old_path, old_fitness, chromosome.path, chromosome.fitness)
        # Сохраняем статистику поколения
        stats = generation.get_population_stats()
        history.append({
            "gen": gen_num,
            "stats": stats,
            "population": [(chrom.path, chrom.fitness) for chrom in generation.population],
            "crossover": crossover_data.copy(),
            "mutation": mutation_data.copy()
        })

    # Переопределяем evolve один раз до цикла
    generation.evolve = modified_evolve

    # Основной цикл генетического алгоритма
    for gen in range(max_generations):
        generation.evolve(gen + 1, mutation_probability)
        print(f"\nСтатистика по поколению {gen + 1}:")
        print(f"  Лучший фитнес: {history[gen]['stats']['best_fitness']}")
        print(f"('+Худший фитнес: {history[gen]['stats']['worst_fitness']}")
        print(f"  Средний фитнес: {history[gen]['stats']['average_fitness']}")

    # Лучшее решение
    best_solution = generation.get_best_chromosome()
    print("\nЛучшее решение:")
    print(f"Путь: {best_solution.path}")
    fitness_str = "-" if best_solution.fitness >= sys.maxsize else f"{best_solution.fitness}"
    print(f"Длина: {fitness_str}")

    # Запускаем визуализацию
    visualize(network, history)

if __name__ == "__main__":
    main()