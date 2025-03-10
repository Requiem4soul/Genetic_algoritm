import random
import sys

class Network:
    def __init__(self, size, density=0.5, max_weight=10, start=None, end=None):
        if size < 10:
            size = 10
        self.size = size
        self.graph = self.generate_upper_triangular_graph(size, density, max_weight)

        # Если начальная вершина не задана, выбираем случайно
        if start is None:
            self.start = random.randint(1, size - 2)
        else:
            self.start = start

        # Если конечная вершина не задана, выбираем случайно
        if end is None:
            self.end = random.randint(self.start + 2, size - 1)
        else:
            self.end = end

        # Инициализируем флаг, который будет показывать, был ли вычислен кратчайший путь
        self.calculated = False
        self.dist_matrix = None
        self.next_node = None

    def generate_upper_triangular_graph(self, size, density, max_weight):
        """Создаёт верхнюю треугольную матрицу смежности."""
        graph = [[None] * size for _ in range(size)]
        for i in range(size):
            for j in range(i, size):  # Теперь заполняем только верхнюю часть
                if i == j:
                    graph[i][j] = 0  # Путь к самому себе = 0
                elif random.random() < density:
                    weight = random.randint(1, max_weight)
                    graph[i][j] = weight  # Заполняем верхний треугольник
        return graph

    def get_weight(self, a, b):
        """Возвращает вес пути между вершинами a и b (или None, если пути нет)."""
        if a > b:
            a, b = b, a  # Теперь меняем местами наоборот
        return self.graph[a][b]

    def print_graph_with_vertices(self):
        """Выводит граф (матрицу смежности) с подписями вершин."""
        # Заголовок (номера столбцов)
        header = "    " + " ".join(f"{i:4}" for i in range(self.size))
        print(header)
        print("    " + "-" * (5 * self.size))

        # Строки матрицы
        for i in range(self.size):
            row = [self.graph[i][j] if self.graph[i][j] is not None else "-" for j in range(self.size)]
            print(f"{i:2} | " + " ".join(f"{x:4}" if x != "-" else "   -" for x in row))

    def floyd(self):
        dist_matrix = [[sys.maxsize] * self.size for _ in range(self.size)]
        next_node = [[None] * self.size for _ in range(self.size)]

        for i in range(self.size):
            for j in range(self.size):
                if i == j:
                    dist_matrix[i][j] = 0
                elif self.graph[i][j] is not None:
                    dist_matrix[i][j] = self.graph[i][j]
                    next_node[i][j] = j

        for k in range(self.size):
            for i in range(self.size):
                for j in range(self.size):
                    if (dist_matrix[i][k] != sys.maxsize and
                            dist_matrix[k][j] != sys.maxsize and
                            dist_matrix[i][j] > dist_matrix[i][k] + dist_matrix[k][j]):
                        dist_matrix[i][j] = dist_matrix[i][k] + dist_matrix[k][j]
                        next_node[i][j] = next_node[i][k]

        self.dist_matrix = dist_matrix
        self.next_node = next_node
        self.calculated = True

        return dist_matrix, next_node

    def reconstruct_path(self, start, end, next_node):
        path = [start]
        if next_node[start][end] is None:
            return []
        while start != end:
            next_step = next_node[start][end]
            if next_step is None:
                return []  # Нет пути
            start = next_step
            path.append(start)
        return path

    def print_optimal_solution(self):
        """
        Выводит оптимальный путь и его длину, используя алгоритм Флойда.
        """
        # Вычисляем кратчайшие пути
        dist_matrix, next_node = self.floyd()

        # Восстанавливаем оптимальный путь
        optimal_path = self.reconstruct_path(self.start, self.end, next_node)
        optimal_fitness = dist_matrix[self.start][self.end]

        # Выводим результат
        print("\nОптимальное решение по Флойду:")
        print(f"Путь: {optimal_path}")
        print(f"Длина: {optimal_fitness}")
