import logging # pylint: disable=C0302
import sqlalchemy

from src.models import User
from src.utils import helpers
from src.utils.db_session import get_db_read_replica
from src.queries.query_helpers import get_current_user_id, populate_user_metadata, paginate_query

logger = logging.getLogger(__name__)

def get_users_cnode(cnode_endpoint_string):
    users = []
    db = get_db_read_replica()
    with db.scoped_session() as session:
        users_res = sqlalchemy.text(
            f"""
            SELECT
            *
            FROM
            (
                SELECT
                "user_id",
                "wallet",
                ("creator_node_endpoints") [1] as "primary",
                ("creator_node_endpoints") [2] as "secondary1",
                ("creator_node_endpoints") [3] as "secondary2"
                FROM
                (
                    SELECT
                    "user_id",
                    "wallet",
                    string_to_array("creator_node_endpoint", ',') as "creator_node_endpoints"
                    FROM
                    "users"
                    WHERE
                    "is_creator" IS TRUE
                    AND "is_current" IS TRUE
                    ORDER BY
                    "user_id" ASC
                ) as "s"
            ) as "t"
            WHERE
            t.primary = :primaryurl
            AND t.secondary1 is not NULL;
            """
        )
        users = session.execute(users_res, { "primaryurl": cnode_endpoint_string }).fetchall()
        users_dict = [dict(row) for row in users]
    return users_dict
