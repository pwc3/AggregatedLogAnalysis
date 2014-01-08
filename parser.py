#!/usr/bin/env python

import argparse
import plistlib
import sqlite3
import sys

def parse_args(argv):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(description="")
    parser.add_argument('filenames',
                        metavar='FILE',
                        nargs='+',
                        help="input filenames")
    return parser.parse_args(argv)

def create_schema(db):
    sql = """
    CREATE TABLE IF NOT EXISTS active_time (
        date, label, duration, UNIQUE (date, label) ON CONFLICT REPLACE
    );

    CREATE TABLE IF NOT EXISTS background_active_time (
        date, label, duration, UNIQUE (date, label) ON CONFLICT REPLACE
    );

    CREATE TABLE IF NOT EXISTS activations (
        date, label, count, UNIQUE (date, label) ON CONFLICT REPLACE
    );

    CREATE TABLE IF NOT EXISTS launches (
        date, label, count, UNIQUE (date, label) ON CONFLICT REPLACE
    );

    DROP VIEW IF EXISTS total_active_time;
    CREATE VIEW total_active_time AS
        SELECT label, SUM(duration) AS duration
        FROM active_time
        GROUP BY label
        ORDER BY duration DESC;

    DROP VIEW IF EXISTS total_background_active_time;
    CREATE VIEW total_background_active_time AS
        SELECT label, SUM(duration) AS duration
        FROM background_active_time
        GROUP BY label
        ORDER BY duration DESC;

    DROP VIEW IF EXISTS total_activations;
    CREATE VIEW total_activations AS
        SELECT label, SUM(count) AS count
        FROM activations
        GROUP BY label
        ORDER BY count DESC;

    DROP VIEW IF EXISTS total_launches;
    CREATE VIEW total_launches AS
        SELECT label, SUM(count) AS count
        FROM launches
        GROUP BY label
        ORDER BY count DESC;

    DROP VIEW IF EXISTS activations_and_launches;
    CREATE VIEW activations_and_launches AS
        SELECT label, SUM(count) AS count
        FROM (
            SELECT * FROM activations
            UNION ALL
            SELECT * FROM launches
        )
        GROUP BY label
        ORDER BY count DESC;

    DROP VIEW IF EXISTS total_time;
    CREATE VIEW total_time AS
        SELECT label, SUM(duration) AS duration
        FROM (
            SELECT * FROM total_active_time
            UNION ALL
            SELECT * FROM total_background_active_time
        )
        GROUP BY label
        ORDER BY duration DESC;
    """

    db.executescript(sql)
    db.commit()

def string_without_prefix(string, prefix):
    if string.startswith(prefix):
        return string[len(prefix):]
    else:
        return string

def update_database(db, plist_filename):
    plist = plistlib.readPlist(plist_filename)
    date = plist['ADStartDate']

    print plist_filename
    print 'Start Date:       ', date, '(UTC)'
    print 'Log Creation Date:', plist['ADLogCreationDate'], '(UTC)'
    print

    prefix_to_sql = {
        'appActivationCount.':
        'INSERT INTO activations (date, label, count) VALUES (?, ?, ?);',

        'appActiveTime.' :
        'INSERT INTO active_time (date, label, duration) VALUES (?, ?, ?);',

        'appBackgroundActiveTime.' :
        'INSERT INTO background_active_time (date, label, duration) VALUES (?, ?, ?);',

        'appLaunchCount.' :
        'INSERT INTO launches (date, label, count) VALUES (?, ?, ?);',
    }

    scalars = plist['ADScalars']
    c = db.cursor()

    for key, value in scalars.iteritems():
        for prefix, sql in prefix_to_sql.iteritems():
            if key.startswith(prefix):
                label = string_without_prefix(key, prefix)
                c.execute(sql, (date, label, value))

    c.close()
    db.commit()

def main(argv=None):
    options = parse_args(argv)

    db = sqlite3.connect('log_aggregated.sqlite3')
    create_schema(db)

    for filename in options.filenames:
        update_database(db, filename)

    db.close()

if __name__ == "__main__":
    sys.exit(main())
