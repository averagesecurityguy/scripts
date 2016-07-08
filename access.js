
try {
    cursor = db.startup_log.findOne();
    print("Hostname: " + cursor['hostname']);
    print("Version: " + cursor['buildinfo']['version']);
} catch(err) {}