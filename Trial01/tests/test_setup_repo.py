from app.repositories import setup_repo


class FakeCursor:
    def __init__(self, database_exists: bool = False):
        self.database_exists = database_exists
        self.executed = []
        self.executemany_calls = []
        self.closed = False

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def executemany(self, query, rows):
        self.executemany_calls.append((query, rows))

    def fetchone(self):
        return ("existing",) if self.database_exists else None

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self, cursor):
        self.fake_cursor = cursor
        self.commits = 0
        self.closed = False

    def cursor(self):
        return self.fake_cursor

    def commit(self):
        self.commits += 1

    def close(self):
        self.closed = True


def test_setup_skips_existing_database(monkeypatch):
    cursor = FakeCursor(database_exists=True)
    connection = FakeConnection(cursor)
    monkeypatch.setattr(
        setup_repo.mysql.connector,
        "connect",
        lambda **_config: connection,
    )

    assert setup_repo.setup_repository() is False
    assert len(cursor.executed) == 1
    assert not cursor.executemany_calls
    assert connection.closed


def test_setup_creates_and_seeds_missing_database(monkeypatch):
    server_cursor = FakeCursor()
    database_cursor = FakeCursor()
    server_connection = FakeConnection(server_cursor)
    database_connection = FakeConnection(database_cursor)
    connections = iter((server_connection, database_connection))
    monkeypatch.setattr(
        setup_repo.mysql.connector,
        "connect",
        lambda **_config: next(connections),
    )

    assert setup_repo.setup_repository() is True
    assert "CREATE DATABASE" in server_cursor.executed[1][0]
    assert "CREATE TABLE" in database_cursor.executed[0][0]
    assert len(database_cursor.executemany_calls[0][1]) == 6
    assert server_connection.closed
    assert database_connection.closed
    assert database_connection.commits == 1
