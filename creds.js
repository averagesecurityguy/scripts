try {
    cursor = db.system.users.find();
    while ( cursor.hasNext() ) {
        c = cursor.next();
        if (c['credentials']['MONGODB-CR']) {
            print(c['user'] + ':' + c['db'] + ':' + c['credentials']['MONGODB-CR']);
        }
        
        if (c['credentials']['SCRAM-SHA-1']) {
            s = c['credentials']['SCRAM-SHA-1'];
            shash = '$scram$' + s['iterationCount'] + '$' + s['salt'].replace('=', '') + '$' + s['storedKey'].replace('=', '');
            print(c['user'] + ':' + c['db'] + ':' + shash);
        }
    }
} catch(err) {}