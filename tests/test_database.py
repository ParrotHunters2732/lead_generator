from database.supabase import Reader
from pytest import raises, fixture, mark
import psycopg2


@fixture()
def base_connection():
    reader = Reader()
    yield reader
    reader.close_all_connection()


def test_blocks_delete(base_connection: Reader):
    with raises(psycopg2.IntegrityError):
        base_connection.user_input_query("DELETE FROM business_list")


def test_blocks_drop(base_connection: Reader):
    with raises(psycopg2.IntegrityError):
        base_connection.user_input_query("DROP TABLE business_list")


def test_blocks_truncate(base_connection: Reader):
    with raises(psycopg2.IntegrityError):
        base_connection.user_input_query("TRUNCATE business_list")


def test_allows_select(base_connection: Reader):
    result = base_connection.user_input_query("SELECT COUNT(*) FROM business_list")
    assert result is not None


def test_query_length_more_than_one(base_connection: Reader):
    prop_query = "SELECT count(*) FROM business_list; SELECT count(*) FROM business_insight_data;"
    with raises(psycopg2.IntegrityError):
        base_connection.user_input_query(prop_query)


@mark.parametrize(
    "query, expected_error",
    [
        ("TABLE Customers", psycopg2.IntegrityError),
        ("DESC Customers;", psycopg2.IntegrityError),
        ("EXPLAIN TABLE Customers;", psycopg2.IntegrityError),
    ],
)
def test_there_is_no_select_or_with(base_connection: Reader, query, expected_error):
    with raises(expected_error):
        base_connection.user_input_query(user_query=query)
