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

    def perform_crossover(self, pairs, crossover_callback=None):
        new_population = []
        for parent1, parent2 in pairs:
            child1, child2, cross_line = parent1.crossover(parent2, random_or_not=True)
            new_population.extend([child1, child2])
            if crossover_callback:
                crossover_callback(parent1, parent2, child1, child2, cross_line)
            else:
                # Оставляем вывод для случаев, когда callback не передан
                def format_fitness(fitness):
                    return "-" if fitness >= sys.maxsize else f"{fitness}"

                print(f"\nРодитель 1: {parent1.path}, фитнес: {format_fitness(parent1.fitness)}")
                print(f"Родитель 2: {parent2.path}, фитнес: {format_fitness(parent2.fitness)}")
                print(f"Линия кроссовера: {cross_line}")
                print(f"Потомок 1: {child1.path}, фитнес: {format_fitness(child1.fitness)}")
                print(f"Потомок 2: {child2.path}, фитнес: {format_fitness(child2.fitness)}")
        return new_population

    def evolve(self, generation_number, mutation_probability=0.5, crossover_callback=None, mutation_callback=None):
        print(f"\nПоколение {generation_number}:")
        chromosome_bank = []
        chromosome_bank.extend(self.population)
        pairs = self.select_pairs_for_crossover()
        new_population = self.perform_crossover(pairs, crossover_callback)
        chromosome_bank.extend(new_population)
        print("\nХромосомы после мутации:")
        mutated_population = []
        for chromosome in new_population:
            old_path = chromosome.path.copy()
            old_fitness = chromosome.fitness
            chromosome.mutation(mutation_probability)
            if chromosome.path != old_path:
                if mutation_callback:
                    mutation_callback(old_path, old_fitness, chromosome.path, chromosome.fitness)
                else:
                    old_fitness_str = "-" if old_fitness >= sys.maxsize else f"{old_fitness}"
                    new_fitness_str = "-" if chromosome.fitness >= sys.maxsize else f"{chromosome.fitness}"
                    print(
                        f"  Хромосома: {old_path} (фитнес: {old_fitness_str}) -> {chromosome.path} (фитнес: {new_fitness_str})")
            mutated_population.append(chromosome)
        chromosome_bank.extend(mutated_population)
        unique_bank = []
        seen_paths = set()
        for chromosome in sorted(chromosome_bank, key=lambda x: x.fitness):
            path_tuple = tuple(chromosome.path)
            if path_tuple not in seen_paths:
                seen_paths.add(path_tuple)
                unique_bank.append(chromosome)
        self.population = unique_bank[:self.population_size]
        if len(self.population) < self.population_size and len(unique_bank) > len(self.population):
            additional_chromosomes = unique_bank[len(self.population):self.population_size]
            self.population.extend(additional_chromosomes)
        print("\nФинальная популяция после эволюции:")
        for i, chromosome in enumerate(self.population):
            fitness_str = "-" if chromosome.fitness >= sys.maxsize else f"{chromosome.fitness}"
            print(f"  Хромосома {i + 1}: {chromosome.path}, фитнес: {fitness_str}")


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
        Возвращает статистику популяции без процентов.
        """
        fitness_values = [chromosome.fitness for chromosome in self.population]
        best_fitness = min(fitness_values)
        worst_fitness = max(fitness_values)
        average_fitness = sum(fitness_values) / len(fitness_values)

        # Функция для форматирования фитнеса
        def format_fitness(fitness):
            if fitness >= sys.maxsize:
                return "-"
            return f"{fitness}"

        return {
            "best_fitness": format_fitness(best_fitness),
            "worst_fitness": format_fitness(worst_fitness),
            "average_fitness": format_fitness(average_fitness),
        }

    def __repr__(self):
        return f"Generation(population_size={self.population_size}, population={self.population})"