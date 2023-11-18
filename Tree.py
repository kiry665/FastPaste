import sqlite3
from PyQt5.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem


def create_tree_from_database(database_file, table_name):
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    # Получаем все записи из таблицы
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    # Создаем словарь, где ключом будет id узла, а значением будет список его дочерних узлов
    nodes = {}
    for row in rows:
        node_id, parent_id, position, node_type, name, data = row
        if parent_id in nodes:
            nodes[parent_id].append(row)
        else:
            nodes[parent_id] = [row]

    # Рекурсивная функция для построения дерева
    def build_tree(parent_item, parent_id):
        if parent_id in nodes:
            for row in nodes[parent_id]:
                node_id, _, _, _, name, _ = row
                item = QTreeWidgetItem(parent_item, [name])
                build_tree(item, node_id)

    # Создаем приложение Qt

    tree = QTreeWidget()
    tree.setColumnCount(1)  # Один столбец для имени узла

    # Строим дерево начиная с корневого узла (узлов с parent_id = 0)
    build_tree(tree, 0)

    # Отображаем дерево
    tree.show()


    # Закрываем соединение с базой данных
    conn.close()
    return tree


# Пример использования
database_file = "Local.db"  # Путь к файлу базы данных SQLite
table_name = "Tree"  # Имя таблицы с деревом

create_tree_from_database(database_file, table_name)