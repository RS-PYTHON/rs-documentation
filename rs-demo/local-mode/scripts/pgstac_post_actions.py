#!/usr/bin/env python3

# Copyright 2023-2026 Airbus, CS Group
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Modify the pgstac database after running it."""

import os

from psycopg.errors import UniqueViolation
from pypgstac.pypgstac import PgstacCLI
from smart_open import open

# Make sure that these env vars are set, see: https://stac-utils.github.io/pgstac/pypgstac/
os.environ["PGHOST"]
os.environ["PGPORT"]
os.environ["PGUSER"]
os.environ["PGDATABASE"]
os.environ["PGPASSWORD"]

# They are use by this pypgstac class.
# Print the version number, it will fail if the connection is not OK
pgstac = PgstacCLI()
print(f"Modify the pgstac database version {pgstac.version!r}")

# Connect to the pgstac database
conn = pgstac._db.connect()
with conn.cursor() as cur:

    # Insert hardcoded stac extension urls
    cur.execute(
        """
        INSERT INTO stac_extensions (url)
        VALUES
            ('https://stac-extensions.github.io/eo/v1.1.0/schema.json'),
            ('https://stac-extensions.github.io/sat/v1.0.0/schema.json'),
            ('https://stac-extensions.github.io/projection/v1.1.0/schema.json'),
            ('https://stac-extensions.github.io/processing/v1.2.0/schema.json'),
            ('https://stac-extensions.github.io/product/v0.1.0/schema.json'),
            ('https://stac-extensions.github.io/sar/v1.0.0/schema.json'),
            ('https://stac-extensions.github.io/raster/v1.1.0/schema.json'),
            ('https://stac-extensions.github.io/authentication/v1.1.0/schema.json'),
            ('https://stac-extensions.github.io/alternate-assets/v1.2.0/schema.json'),
            ('https://stac-extensions.github.io/timestamps/v1.1.0/schema.json'),
            ('https://stac-extensions.github.io/file/v2.1.0/schema.json')
        ON CONFLICT DO NOTHING;
        """,
    )
    conn.commit()

    # Load the stac extension contents.

    # This does not work, we need to replace 'pgstac._db.query(' by 'cur.execute',
    # I don't know why, so I just copy/paste the code below.
    # pgstac.loadextensions()
    urls = pgstac._db.query(
        """
            SELECT url FROM stac_extensions WHERE content IS NULL;
        """,
    )
    if urls:
        for u in urls:
            url = u[0]
            try:
                with open(url) as f:
                    content = f.read()
                    # pgstac._db.query( # this does not work
                    cur.execute(
                        """
                            UPDATE pgstac.stac_extensions
                            SET content=%s
                            WHERE url=%s
                            ;
                        """,
                        [content, url],
                    )
                    conn.commit()
            except Exception as e:
                print(e)

    # Insert hardcoded queryables
    try:
        for queryable in (
            "eo:snow_cover",
            "sat:absolute_orbit",
            "sat:relative_orbit",
            "processing:level",
            "processing:facility",
            "processing:datetime",
            "processing:version",
            "product:type",
            "product:timeliness",
            "product:timeliness_category",
            "sar:instrument_mode",
            "published",
            "expires",
            "unpublished",
        ):
            cur.execute(
                """
                INSERT INTO queryables (name)
                SELECT %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM queryables WHERE name = %s
                );
                """,
                (queryable, queryable),
            )
        conn.commit()

    # Ignore duplicates
    except UniqueViolation:
        pass

    # Add externalIds support for CQL2 search:
    # - Build a token array from externalIds (scheme:value, value, scheme)
    # - Use a_overlaps() on the token array for fast matching
    cur.execute(
        """
        CREATE OR REPLACE FUNCTION pgstac.external_ids_tokens(ext jsonb) RETURNS jsonb AS $$
            SELECT CASE
                WHEN ext IS NULL OR jsonb_typeof(ext) <> 'array' THEN '[]'::jsonb
                ELSE COALESCE(
                    (
                        SELECT jsonb_agg(DISTINCT token)
                        FROM (
                            SELECT CASE
                                WHEN scheme IS NOT NULL AND scheme <> '' AND value IS NOT NULL AND value <> ''
                                THEN scheme || ':' || value
                            END AS token
                            FROM jsonb_to_recordset(ext) AS x(scheme text, value text)
                            UNION ALL
                            SELECT value
                            FROM jsonb_to_recordset(ext) AS x(scheme text, value text)
                            WHERE value IS NOT NULL AND value <> ''
                            UNION ALL
                            SELECT scheme
                            FROM jsonb_to_recordset(ext) AS x(scheme text, value text)
                            WHERE scheme IS NOT NULL AND scheme <> ''
                        ) tokens
                        WHERE token IS NOT NULL AND token <> ''
                    ),
                    '[]'::jsonb
                )
            END;
        $$ LANGUAGE SQL IMMUTABLE;
        """,
    )
    conn.commit()

    try:
        cur.execute(
            """
            INSERT INTO queryables (name, definition, property_path)
            SELECT
                'externalIds',
                '{"title": "externalIds", "description": "externalIds", "type": "string"}',
                'pgstac.external_ids_tokens(content->''properties''->''externalIds'')'
            WHERE NOT EXISTS (
                SELECT 1 FROM queryables WHERE name = 'externalIds'
            );
            """,
        )
        conn.commit()
    except UniqueViolation:
        pass

    # Add 'format' and 'pattern' for expires to have better timestamp queries
    try:
        cur.execute(
            """
            UPDATE queryables
            SET definition = '{
                "type": "string",
                "format": "date-time",
                "pattern": "(\\\\+00:00|Z)$"
            }'::jsonb
            WHERE name = 'expires';
            """,
        )
        conn.commit()

    except Exception:
        conn.rollback()
        raise
