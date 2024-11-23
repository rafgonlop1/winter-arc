import unittest
from winter.modules.database import get_connection


class TestDatabaseConnection(unittest.TestCase):
    def test_connection(self):
        connection = get_connection()
        self.assertIsNotNone(connection, "Failed to connect to the database.")
        if connection:
            connection.close()


if __name__ == '__main__':
    unittest.main()
