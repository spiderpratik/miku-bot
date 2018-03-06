import pymysql
from pymysql.err import OperationalError, InterfaceError

class dbHelper:
    def __init__(self):
        self.db = pymysql.connect("localhost", "miku", "discord", "mikuDB")


    def report(self, reporter, reportee, t, retry = True):
        try:
            with self.db.cursor() as cursor:
                affectedRowsCount = cursor.execute("INSERT INTO reports VALUES ('%s', '%s', 1, '%s') ON DUPLICATE KEY UPDATE count = count + 1, last_ts = '%s'" % (reporter, reportee, t, t))
                self.db.commit()
            return affectedRowsCount
        except (OperationalError, InterfaceError) as e:
            if retry:
                self.__init__()
                return self.report(reporter, reportee, t, False)
            else:
                raise


    def request(self, requestor, requestee, t, retry = True):
        try:
            with self.db.cursor() as cursor:
                affectedRowsCount = cursor.execute("INSERT INTO requests VALUES ('%s', '%s', '%s') ON DUPLICATE KEY UPDATE ts = '%s'" % (requestor, requestee, t, t))
                self.db.commit()
        except (OperationalError, InterfaceError) as e:
            if retry:
                self.__init__()
                return self.request(requestor, requestee, t, False)
            else:
                raise


    def unreport(self, reporter, reportee, retry = True):
        try:
            with self.db.cursor() as cursor:
                # affectedRowsCount = cursor.execute("UPDATE reports SET count = count - 1 WHERE reporter = '%s' AND reportee = '%s' AND count > 0" % (reporter, reportee))
                affectedRowsCount = cursor.execute("DELETE FROM reports WHERE reporter = '%s' AND reportee = '%s'" % (reporter, reportee))
                self.db.commit()
            return affectedRowsCount
        except (OperationalError, InterfaceError) as e:
            if retry:
                self.__init__()
                return self.unreport(reporter, reportee, False)
            else:
                raise


    def get_report(self, reporter, reportee, retry = True):
        try:
            with self.db.cursor() as cursor:
                cursor.execute("SELECT count, last_ts FROM reports WHERE reporter = '%s' AND reportee = '%s'" % (reporter, reportee))
                ans = cursor.fetchone()
            return (reporter, reportee, "0", "") if ans is None else (reporter, reportee, str(ans[0]), "Last reported at " + ans[1])
        except (OperationalError, InterfaceError) as e:
            if retry:
                self.__init__()
                return self.get_report(reporter, reportee, False)
            else:
                raise


    def get_report_aggregated(self, user, retry = True):
        try:
            with self.db.cursor() as cursor:
                cursor.execute("SELECT SUM(count) FROM reports WHERE reportee = '%s'" % (user))
                ans = cursor.fetchone()[0]
                got_reported = "0" if ans is None else str(ans)
            with self.db.cursor() as cursor:
                cursor = self.db.cursor()
                cursor.execute("SELECT SUM(count) FROM reports WHERE reporter = '%s'" % (user))
                ans = cursor.fetchone()[0]
                reported_others = "0" if ans is None else str(ans)
            return (user, got_reported, reported_others)
        except (OperationalError, InterfaceError) as e:
            if retry:
                self.__init__()
                return self.get_report_aggregated(user, False)
            else:
                raise


    def get_report_verbose(self, mode, user, retry = True):
        try:
            with self.db.cursor() as cursor:
                cursor.execute("SELECT %s, count FROM reports WHERE %s = '%s' AND count > 0" % (self.flipMode(mode), mode, user))
            return ", ".join(("%s (%d)" % i) for i in cursor.fetchall())
        except (OperationalError, InterfaceError) as e:
            if retry:
                self.__init__()
                return self.get_report_verbose(mode, user, False)
            else:
                raise


    def get_requests_from(self, requestor, retry = True):
        try:
            with self.db.cursor() as cursor:
                cursor.execute("SELECT requestee, ts FROM requests WHERE requestor = '%s'" % (requestor))
            return ", ".join(("%s (%s)" % i) for i in cursor.fetchall())
        except (OperationalError, InterfaceError) as e:
            if retry:
                self.__init__()
                return self.get_requests_from(requestor, False)
            else:
                raise


    def get_requests_to(self, requestee, retry = True):
        try:
            with self.db.cursor() as cursor:
                cursor.execute("SELECT requestor, ts FROM requests WHERE requestee = '%s'" % (requestee))
            return ", ".join(("%s (%s)" % i) for i in cursor.fetchall())
        except (OperationalError, InterfaceError) as e:
            if retry:
                self.__init__()
                return self.get_requests_to(requestee, False)
            else:
                raise


    def delete_request(self, requestor, requestee, retry = True):
        try:
            with self.db.cursor() as cursor:
                affectedRowsCount = cursor.execute("DELETE FROM requests WHERE requestor = '%s' AND requestee = '%s'" % (requestor, requestee))
                self.db.commit()
            return affectedRowsCount
        except (OperationalError, InterfaceError) as e:
            if retry:
                self.__init__()
                return self.delete_request(requestor, requestee, False)
            else:
                raise


    def reset_reports(self, mode, user):
        with self.db.cursor() as cursor:
            affectedRowsCount = cursor.execute("DELETE FROM reports WHERE %s = '%s'" % (mode, user))
            self.db.commit()
            return affectedRowsCount


    def flipMode(self, mode):
        if mode == "reporter":
            return "reportee"
        elif mode == "reportee":
            return "reporter"
        else:
            return None



# MySQL DB Schema
# ---------------
# Database: mikuDB
# Table: reports
#
#+----------+----------+------+-----+------------------------+-------+
#| Field    | Type     | Null | Key | Default                | Extra |
#+----------+----------+------+-----+------------------------+-------+
#| reporter | char(40) | NO   | PRI |                        |       |
#| reportee | char(40) | NO   | PRI |                        |       |
#| count    | int(11)  | NO   |     | 0                      |       |
#| last_ts  | char(25) | NO   |     | the beginning of time! |       |
#+----------+----------+------+-----+------------------------+-------+
#
#
# Table: requests
#
#+-----------+----------+------+-----+------------------------+-------+
#| Field     | Type     | Null | Key | Default                | Extra |
#+-----------+----------+------+-----+------------------------+-------+
#| requestor | char(30) | NO   | PRI | NULL                   |       |
#| requestee | char(30) | NO   | PRI | NULL                   |       |
#| ts        | char(25) | NO   |     | the beginning of time! |       |
#+-----------+----------+------+-----+------------------------+-------+
#

