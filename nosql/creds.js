/*
 * This software is Copyright (c) 2016 AverageSecurityGuy <stephen at averagesecurityguy.info>,
 * and it is hereby released to the general public under the following terms:
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted.
 */

 try {
    cursor = db.system.users.find();
    while ( cursor.hasNext() ) {
        c = cursor.next();
        if (c['credentials']['MONGODB-CR']) {
            print(c['user'] + ':' + c['db'] + ':' + c['credentials']['MONGODB-CR']);
        }

        if (c['credentials']['SCRAM-SHA-1']) {
            s = c['credentials']['SCRAM-SHA-1'];
            shash = '$scram$' + s['iterationCount'] + '$' + s['salt'] + '$' + s['storedKey'];
            print(c['user'] + ':' + c['db'] + ':' + shash);
        }
    }
} catch(err) {}
