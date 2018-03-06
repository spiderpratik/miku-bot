import pymysql
from pymysql.err import OperationalError, InterfaceError

class dbHelper:
    def __init__(self):
        self.db = pymysql.connect("localhost", "miku", "discord", "mikuDB")


    def report(self, reporter, reportee, t, retry = True):
        try:
            with self.db.cursor() as cursor:
                affectedRowsCount = cursor.execute("INSERT INTO reports VALUES ('%s', '%s', 1, '%s', NULL) ON DUPLICATE KEY UPDATE count = count + 1, report_ts = '%s'" % (reporter, reportee, t, t))
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
                affectedRowsCount = cursor.execute("UPDATE reports SET request_ts = '%s' WHERE reporter = '%s' AND reportee = '%s'" % (t, requestee, requestor))
                self.db.commit()
            return affectedRowsCount
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
                affectedRowsCount = cursor.execute("DELETE FROM reports WHERE reporter = '%s' AND reportee = '%s' AND count > 0" % (reporter, reportee))
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
                cursor.execute("SELECT count, report_ts FROM reports WHERE reporter = '%s' AND reportee = '%s'" % (reporter, reportee))
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
                cursor.execute("SELECT reporter, request_ts FROM reports WHERE reportee = '%s' AND request_ts IS NOT NULL" % (requestor))
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
                cursor.execute("SELECT reportee, request_ts FROM reports WHERE reporter = '%s' AND request_ts IS NOT NULL" % (requestee))
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
                affectedRowsCount = cursor.execute("UPDATE reports SET request_ts = NULL WHERE reporter = '%s' AND reportee = '%s'" % (requestee, requestor))
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
#+------------+----------+------+-----+------------------------+-------+
#| Field      | Type     | Null | Key | Default                | Extra |
#+------------+----------+------+-----+------------------------+-------+
#| reporter   | char(40) | NO   | PRI |                        |       |
#| reportee   | char(40) | NO   | PRI |                        |       |
#| count      | int(11)  | NO   |     | 0                      |       |
#| report_ts  | char(25) | NO   |     | the beginning of time! |       |
#| request_ts | char(25) | YES  |     | the beginning of time! |       |
#+------------+----------+------+-----+------------------------+-------+
#

