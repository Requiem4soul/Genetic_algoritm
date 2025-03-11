import random
import sys

class Chromosome:
    def __init__(self, path, network):
        """
        path: путь хромосомы (список вершин)
        network: объект сети
        """
        self.path = path
        self.network = network
        self.fitness = None
        self.calculate_fitness()

    def calculate_fitness(self):
        """
        Рассчитывает фитнес хромосомы.
        Если путь неправильный (не совпадает с начальной/конечной точкой), присваиваем максимальный фитнес.
        Если путь существует и правильный, то считаем его длину.
        """
        start = self.network.start
        end = self.network.end

        if self.path[0] != start or self.path[-1] != end:
            self.fitness = sys.maxsize  # Если путь неправильный, ставим максимально возможный фитнес
            return

        total_path_length = 0
        for i in range(len(self.path) - 1):
            if self.network.get_weight(self.path[i], self.path[i+1]) is None:
                self.fitness = sys.maxsize
                return
            total_path_length += self.network.get_weight(self.path[i], self.path[i+1])

        self.fitness = total_path_length  # Чем меньше путь, тем лучше фитнес

    def __repr__(self):
        return f"Chromosome(path={self.path}, fitness={self.fitness})"

    def mutation(self, mutation_probability=0.5):
        """Мутация без проверки рёбер. Заменяем вершины на случайные."""
        start = self.network.start
        end = self.network.end

        # Пример случайной замены вершины на пути (кроме начальной и конечной)
        path = self.path[1:-1]  # Оставляем только промежуточные вершины
        for i in range(len(path)):
            if random.random() < mutation_probability:  # Используем заданную вероятность мутации вершины
                new_vertex = random.randint(start + 1, end - 1)  # Генерируем случайную вершину от start+1 до end-1
                path[i] = new_vertex  # Заменяем на случайную вершину

        self.path = [start] + path + [end]  # Восстанавливаем начальную и конечную вершины
        self.calculate_fitness()  # Пересчитываем фитнес после мутации

    def crossover(self, other, random_or_not=False, cross_line=None):
        """
        Кроссовер с возможностью случайной точки разбиения.
        random_or_not: если True, точка разбиения выбирается случайно.
        cross_line: если указано, то используется точка разбиения, иначе случайная.
        """
        start = self.network.start
        end = self.network.end

        # Промежуточные вершины (без start и end)
        path1 = self.path[1:-1]
        path2 = other.path[1:-1]
        max_length = max(len(path1), len(path2))

        # Определяем точку разбиения
        if random_or_not and max_length > 0:
            line_to_cross = random.randint(0, max_length - 1)
        elif cross_line is not None and 0 <= cross_line < max_length:
            line_to_cross = cross_line
        else:
            line_to_cross = random.randint(0, max_length - 1) if max_length > 0 else 0

        if line_to_cross == 0:
            line_to_cross = 2

        # Создаём новые промежуточные пути
        new_path1 = path1[:]
        new_path2 = path2[:]

        # Обмениваем части после точки разбиения
        for i in range(line_to_cross, max_length):
            if i < len(path1) and i < len(path2):
                new_path1[i], new_path2[i] = new_path2[i], new_path1[i]
            elif i < len(path1):  # Если path1 длиннее, оставляем остаток
                new_path1[i] = path1[i]
            elif i < len(path2):  # Если path2 длиннее, оставляем остаток
                new_path2[i] = path2[i]

        # Собираем полные пути с начальной и конечной точками
        child_path1 = [start] + new_path1 + [end]
        child_path2 = [start] + new_path2 + [end]

        # Создаём потомков
        child1 = Chromosome(child_path1, self.network)
        child2 = Chromosome(child_path2, self.network)

        return child1, child2, line_to_cross
