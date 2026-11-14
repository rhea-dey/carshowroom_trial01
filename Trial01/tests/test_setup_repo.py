from app.backend.repositories.setup_repo import setup_repo


class FakeCursor:
    def __init__(self, database_exists=False, tables=()):
        self.database_exists = database_exists
        self.tables = tables
        self.executed = []
        self.executemany_calls = []
        self.closed = False

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def executemany(self, query, rows):
        self.executemany_calls.append((query, rows))

    def fetchone(self):
        return ("existing",) if self.database_exists else None

    def fetchall(self):
        return [(table,) for table in self.tables]

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


def _mock_connections(monkeypatch, *connections):
    remaining = iter(connections)
    monkeypatch.setattr(
        setup_repo.mysql.connector,
        "connect",
        lambda **_config: next(remaining),
    )


def _assert_image_rows(cursor, call_index, table_name, expected_filenames):
    query, rows = cursor.executemany_calls[call_index]
    assert f"INSERT INTO {table_name}" in query
    assert {row[1] for row in rows} == set(expected_filenames)
    assert all(row[2] == "image/png" and row[3] for row in rows)


def test_setup_skips_when_database_and_tables_exist(monkeypatch):
    required_tables = set(setup_repo.TABLE_DEFINITIONS)
    server_connection = FakeConnection(FakeCursor(database_exists=True))
    database_cursor = FakeCursor(tables=required_tables)
    database_connection = FakeConnection(database_cursor)
    _mock_connections(monkeypatch, server_connection, database_connection)

    assert setup_repo.setup_repository() is False
    assert database_cursor.executed == [("SHOW TABLES", None)]
    assert not database_cursor.executemany_calls
    assert server_connection.closed
    assert database_connection.closed


def test_setup_creates_missing_tables_on_existing_database(monkeypatch):
    server_connection = FakeConnection(FakeCursor(database_exists=True))
    database_cursor = FakeCursor(tables={"cars"})
    database_connection = FakeConnection(database_cursor)
    _mock_connections(monkeypatch, server_connection, database_connection)

    assert setup_repo.setup_repository() is True
    created_tables = [
        query.split("CREATE TABLE ", 1)[1].split(" ", 1)[0]
        for query, _params in database_cursor.executed
        if "CREATE TABLE " in query
    ]
    assert set(created_tables) == set(setup_repo.TABLE_DEFINITIONS) - {"cars"}
    assert len(database_cursor.executemany_calls) == 3
    assert "users" in database_cursor.executemany_calls[0][0]
    _assert_image_rows(
        database_cursor,
        1,
        "car_images",
        {
            "panther-gls-130.png",
            "rockrover-rl.png",
            "falcon-x.png",
            "quid-z-300.png",
            "rlv-minora.png",
            "fenty-500.png",
        },
    )
    _assert_image_rows(
        database_cursor,
        2,
        "car_custom_images",
        {
            "panther-gls-130-custom.png",
            "rockrover-rl-custom.png",
            "falcon-x-custom.png",
            "custom-z-custom.png",
            "rlv-minora-custom.png",
            "fenty-500-custom.png",
        },
    )
    assert server_connection.closed
    assert database_connection.closed


def test_setup_creates_database_tables_and_seed_data_when_missing(monkeypatch):
    server_cursor = FakeCursor()
    database_cursor = FakeCursor()
    server_connection = FakeConnection(server_cursor)
    database_connection = FakeConnection(database_cursor)
    _mock_connections(monkeypatch, server_connection, database_connection)

    assert setup_repo.setup_repository() is True
    assert "CREATE DATABASE" in server_cursor.executed[1][0]
    assert len(database_cursor.executemany_calls[0][1]) == 6
    assert len(database_cursor.executemany_calls[1][1]) == 2
    _assert_image_rows(
        database_cursor,
        2,
        "car_images",
        {
            "panther-gls-130.png",
            "rockrover-rl.png",
            "falcon-x.png",
            "quid-z-300.png",
            "rlv-minora.png",
            "fenty-500.png",
        },
    )
    _assert_image_rows(
        database_cursor,
        3,
        "car_custom_images",
        {
            "panther-gls-130-custom.png",
            "rockrover-rl-custom.png",
            "falcon-x-custom.png",
            "custom-z-custom.png",
            "rlv-minora-custom.png",
            "fenty-500-custom.png",
        },
    )
    assert server_connection.closed
    assert database_connection.closed
    assert database_connection.commits == 1
