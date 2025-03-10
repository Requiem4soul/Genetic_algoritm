import random
import sys
from algorithm.chromosome import Chromosome


class Generation:
    def __init__(self, network, k=1, min_population=10, max_population=100, min_length=3, max_length=None):
        """
        Инициализация поколения.
        :param network: объект сети, в которой будут создаваться хромосомы
        :param k: коэффициент для расчёта population_size (количество хромосом на одну вершину)
        :param min_population: минимальное количество хромосом
        :param max_population: максимальное количество хромосом
        :param min_length: минимальная длина хромосомы (должна быть >= 2)
        :param max_length: максимальная длина хромосомы (если None, будет вычислена автоматически)
        """
        self.network = network
        self.population_size = self.calculate_population_size(network.size, k, min_population, max_population)
        self.min_length = max(min_length, 2)
        self.max_length = max_length if max_length is not None else min(2 * network.size, 20)

        # Вычисляем оптимальное решение один раз
        dist_matrix, _ = network.floyd()
        self.optimal_fitness = dist_matrix[network.start][network.end]

        # Создаём начальную популяцию
        self.population = self.create_initial_population()

    def calculate_population_size(self, number_of_vertices, k, min_population, max_population):
        """
        Вычисляет population_size на основе количества вершин.
        :param number_of_vertices: количество вершин в графе
        :param k: коэффициент для расчёта population_size
        :param min_population: минимальное количество хромосом
        :param max_population: максимальное количество хромосом
        :return: population_size
        """
        return min(max_population, max(min_population, k * number_of_vertices))

    def create_initial_population(self):
        """Создание начальной популяции с хромосомами разной длины."""
        population = []
        for _ in range(self.population_size):
            chromosome_length = random.randint(self.min_length, self.max_length)
            path = self.generate_random_path(chromosome_length)
            chromosome = Chromosome(path, self.network)
            population.append(chromosome)
        return population

    def generate_random_path(self, length):
        """Генерация случайного пути для хромосомы заданной длины."""
        start = self.network.start
        end = self.network.end
        intermediate = random.sample(range(0, self.network.size), length - 2)  # Выбираем уникальные вершины
        return [start] + intermediate + [end]

    def remove_duplicates(self):
        """Удаляет дубликаты хромосом из популяции."""
        unique_population = []
        seen_paths = set()
        for chromosome in self.population:
            path_tuple = tuple(chromosome.path)
            if path_tuple not in seen_paths:
                seen_paths.add(path_tuple)
                unique_population.append(chromosome)
        self.population = unique_population

    def select_best(self):
        """Отбор лучших хромосом в популяции."""
        sorted_population = sorted(self.population, key=lambda x: x.fitness)
        self.population = sorted_population[:self.population_size]

    def select_pairs_for_crossover(self):
        """
        Выбирает пары для кроссовера, исключая одинаковые хромосомы.
        :return: список пар для кроссовера
        """
        sorted_population = sorted(self.population, key=lambda x: x.fitness)
        num_pairs = max(1, int(self.population_size * 0.2))  # 20% популяции
        parents = sorted_population[:num_pairs * 2]  # Берём лучших
        pairs = []
        used_indices = set()  # Отслеживаем использованные хромосомы

        for i in range(0, len(parents), 2):
            parent1 = parents[i]
            # Ищем пару, которая ещё не использовалась
            j = i + 1
            while j < len(parents) and (j in used_indices or parents[j].path == parent1.path):
                j += 1
            parent2 = parents[j] if j < len(parents) else parents[0]  # Если не нашли, берём первую
            if parent1.path != parent2.path and i not in used_indices and j not in used_indices:
                pairs.append((parent1, parent2))
                used_indices.add(i)
                used_indices.add(j)

        return pairs

    def perform_crossover(self, pairs):
        """
        Выполняет кроссовер для выбранных пар и возвращает новую популяцию.
        """
        new_population = []

        # Выполняем кроссовер для каждой пары
        for parent1, parent2 in pairs:
            child1, child2, cross_line = parent1.crossover(parent2, random_or_not=True)
            new_population.extend([child1, child2])

            # Выводим информацию о кроссовере
            print(f"\nРодитель 1: {parent1.path}, фитнес: {parent1.fitness}")
            print(f"Родитель 2: {parent2.path}, фитнес: {parent2.fitness}")
            print(f"Линия кроссовера: {cross_line}")
            print(f"Потомок 1: {child1.path}, фитнес: {child1.fitness}")
            print(f"Потомок 2: {child2.path}, фитнес: {child2.fitness}")

        return new_population

    def evolve(self, generation_number, mutation_probability=0.5, elitism_ratio=0.1):
        """
        Эволюция популяции: отбор, кроссовер, мутация с добавлением элитизма.
        :param generation_number: номер текущего поколения
        :param mutation_probability: вероятность мутации
        :param elitism_ratio: доля элитных хромосом (например, 0.1 для 10%)
        """
        print(f"\nПоколение {generation_number}:")

        # "Банк" хромосом для хранения всех кандидатов
        chromosome_bank = []

        # 1. Сохраняем исходную популяцию (до кроссинговера)
        chromosome_bank.extend(self.population)

        # 2. Выполняем кроссинговер и сохраняем потомков
        pairs = self.select_pairs_for_crossover()
        new_population = self.perform_crossover(pairs)
        chromosome_bank.extend(new_population)  # Добавляем потомков после кроссинговера

        # 3. Применяем мутацию с выводом изменений
        print("\nХромосомы после мутации:")
        mutated_population = []
        for chromosome in new_population:
            old_path = chromosome.path.copy()  # Сохраняем исходный путь
            old_fitness = chromosome.fitness  # Сохраняем исходный фитнес
            chromosome.mutation(mutation_probability)  # Применяем мутацию
            if chromosome.path != old_path:  # Выводим только если путь изменился
                print(
                    f"  Хромосома: {old_path} (фитнес: {old_fitness}) -> {chromosome.path} (фитнес: {chromosome.fitness})")
            mutated_population.append(chromosome)
        chromosome_bank.extend(mutated_population)  # Добавляем хромосомы после мутации

        # 4. Удаляем дубликаты из банка (по пути)
        unique_bank = []
        seen_paths = set()
        for chromosome in chromosome_bank:
            path_tuple = tuple(chromosome.path)
            if path_tuple not in seen_paths:
                seen_paths.add(path_tuple)
                unique_bank.append(chromosome)
        chromosome_bank = unique_bank

        # 5. Сортируем по фитнесу и обрезаем до population_size
        chromosome_bank.sort(key=lambda x: x.fitness)
        self.population = chromosome_bank[:self.population_size]

        # Выводим финальную популяцию
        print("\nФинальная популяция после эволюции:")
        for i, chromosome in enumerate(self.population):
            print(f"  Хромосома {i + 1}: {chromosome.path}, фитнес: {chromosome.fitness}")


    def apply_mutations(self, population, mutation_probability):
        """
        Применяет мутации к популяции.
        """
        for chromosome in population:
            chromosome.mutation(mutation_probability)

    def select_elites(self, elitism_ratio):
        """
        Выбирает лучшие хромосомы из текущего поколения.
        :param elitism_ratio: доля элитных хромосом
        :return: список элитных хромосом
        """
        num_elites = int(self.population_size * elitism_ratio)
        sorted_population = sorted(self.population, key=lambda x: x.fitness)
        return sorted_population[:num_elites]

    def trim_population(self, population):
        """
        Обрезает популяцию до population_size, оставляя лучшие хромосомы.
        """
        population.sort(key=lambda x: x.fitness)
        return population[:self.population_size]

    def get_best_chromosome(self):
        """Возвращает лучшую хромосому в текущем поколении."""
        return min(self.population, key=lambda x: x.fitness)

    def get_population_stats(self):
        """
        Возвращает статистику популяции в процентах относительно оптимального решения.
        """
        if self.optimal_fitness == 0:
            return {
                "best_percent": 0,
                "worst_percent": 0,
                "average_percent": 0,
            }

        fitness_values = [chromosome.fitness for chromosome in self.population]
        best_fitness = min(fitness_values)
        worst_fitness = max(fitness_values)
        average_fitness = sum(fitness_values) / len(fitness_values)

        # Функция для форматирования фитнеса
        def format_fitness(fitness):
            if fitness == sys.maxsize or fitness > sys.maxsize or fitness is float:
                return "-"
            return f"{fitness}"

        # Функция для форматирования процентов
        def format_percent(fitness):
            if fitness == sys.maxsize or fitness > sys.maxsize or fitness is float:
                return "0.00%"
            return f"{(fitness / self.optimal_fitness) * 100:.2f}%"

        return {
            "best_fitness": format_fitness(best_fitness),
            "best_percent": format_percent(best_fitness),
            "worst_fitness": format_fitness(worst_fitness),
            "worst_percent": format_percent(worst_fitness),
            "average_fitness": format_fitness(average_fitness),
            "average_percent": format_percent(average_fitness),
        }

    def __repr__(self):
        return f"Generation(population_size={self.population_size}, population={self.population})"