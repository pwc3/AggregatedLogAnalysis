import socket, sqlite3

def print_int_results(db, sql):
    c = db.cursor()
    result = c.execute(sql)
    for row in result:
        print '%7d %s' % row

    print
    c.close()

def print_results(db, sql):
    c = db.cursor()
    result = c.execute(sql)
    for row in result:
        print '\t'.join(row)

    print
    c.close()

if __name__ == '__main__':
    hostname = socket.gethostname().replace(' ', '_')
    db = sqlite3.connect('%s_log_aggregated.sqlite3' % hostname)

    print 'Total Active Time:'
    print_int_results(db,
                      'SELECT duration, name FROM total_active_time;')

    print 'Total Background Active Time:'
    print_int_results(db,
                      'SELECT duration, name FROM total_background_active_time;')

    print 'Total Activations:'
    print_int_results(db,
                      'SELECT count, name FROM total_activations;')

    print 'Total Launches:'
    print_int_results(db,
                      'SELECT count, name FROM total_launches;')

    print 'Dates:'
    print_results(db,
                  'SELECT DISTINCT date FROM stats ORDER BY date;')

    db.close()
