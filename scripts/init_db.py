from backend.database.connection import DATABASE_PATH
from backend.database.initializer import initialize_database


def main() -> None:
    table_counts = initialize_database()

    print(f"Database initialized: {DATABASE_PATH}")
    for table_name, row_count in table_counts.items():
        print(f"- {table_name}: {row_count}")


if __name__ == "__main__":
    main()
