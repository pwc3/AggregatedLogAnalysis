#!/usr/bin/env python

import argparse
import codecs
import plistlib
import socket
import sqlite3
import sys

PREFIX_TO_TYPE = {
    'appActivationCount.': 'activations',
    'appActiveTime.': 'active time',
    'appBackgroundActiveTime.': 'background active time',
    'appLaunchCount.': 'launches',
}

def create_schema(db):
    sql = """
    CREATE TABLE IF NOT EXISTS stats (
        date TEXT,
        type TEXT,
        name TEXT,
        value INTEGER,
        UNIQUE (type, name, date) ON CONFLICT REPLACE
    );

    CREATE TABLE IF NOT EXISTS plists (
        filename TEXT,
        content TEXT,
        UNIQUE (filename) ON CONFLICT REPLACE
    );

    DROP VIEW IF EXISTS total_active_time;
    CREATE VIEW total_active_time AS
        SELECT name, SUM(value) AS duration
        FROM stats
        WHERE type = 'active time'
        GROUP BY name
        ORDER BY SUM(value) DESC;

    DROP VIEW IF EXISTS total_background_active_time;
    CREATE VIEW total_background_active_time AS
        SELECT name, SUM(value) AS duration
        FROM stats
        WHERE type = 'background active time'
        GROUP BY name
        ORDER BY SUM(value) DESC;

    DROP VIEW IF EXISTS total_activations;
    CREATE VIEW total_activations AS
        SELECT name, SUM(value) AS count
        FROM stats
        WHERE type = 'activations'
        GROUP BY name
        ORDER BY SUM(value) DESC;

    DROP VIEW IF EXISTS total_launches;
    CREATE VIEW total_launches AS
        SELECT name, SUM(value) AS count
        FROM stats
        WHERE type = 'launches'
        GROUP BY name
        ORDER BY SUM(value) DESC;

    DROP VIEW IF EXISTS activations_and_launches;
    CREATE VIEW activations_and_launches AS
        SELECT name, SUM(value) AS count
        FROM stats
        WHERE type = 'launches' OR type = 'activations'
        GROUP BY name
        ORDER BY SUM(value) DESC;

    DROP VIEW IF EXISTS total_time;
    CREATE VIEW total_time AS
        SELECT name, SUM(value) AS count
        FROM stats
        WHERE type = 'active time' OR type = 'background active time'
        GROUP BY name
        ORDER BY SUM(value) DESC;
    """

    db.executescript(sql)
    db.commit()

def string_without_prefix(string, prefix):
    if string.startswith(prefix):
        return string[len(prefix):]
    else:
        return string

def update_database(db, plist_string):
    plist = plistlib.readPlistFromString(plist_string)

    start_date = plist['ADStartDate']
    create_date = plist['ADLogCreationDate']

    plist_filename = 'log-aggregated-%s.plist' % create_date.strftime('%Y-%m-%d-%H%M%S')
    print plist_filename

    print 'Start Date:       ', start_date, '(UTC)'
    print 'Log Creation Date:', create_date, '(UTC)'
    print

    scalars = plist['ADScalars']
    c = db.cursor()

    sql = 'INSERT INTO plists (filename, content) VALUES (?, ?);'
    c.execute(sql, (plist_filename, plist_string))

    sql = 'INSERT INTO stats (date, type, name, value) VALUES (?, ?, ?, ?);'

    for key, value in scalars.iteritems():
        for prefix, typ in PREFIX_TO_TYPE.iteritems():
            if key.startswith(prefix):
                name = string_without_prefix(key, prefix)
                c.execute(sql, (start_date, typ, name, value))

    c.close()
    db.commit()

def update_database_from_clipboard(db):
    try:
        import clipboard
    except ImportError:
        return

    plist_string = clipboard.get()
    update_database(db, plist_string)

def parse_args(argv):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(description="")
    parser.add_argument('filenames',
                        metavar='FILE',
                        nargs='*',
                        help="input filenames")
    return parser.parse_args(argv)

def main(argv=None):
    options = parse_args(argv)

    hostname = socket.gethostname().replace(' ', '_')
    db = sqlite3.connect('%s_log_aggregated.sqlite3' % hostname)
    create_schema(db)

    try:
        if options.filenames:
            for filename in options.filenames:
                with codecs.open(filename, 'r', 'utf-8') as fh:
                    plist_string = fh.read()
                    update_database(db, plist_string)
        else:
            update_database_from_clipboard(db)

    finally:
        db.close()

if __name__ == "__main__":
    main()
