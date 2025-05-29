from __init__ import CURSOR, CONN
from employee import Employee

class Review:
    # Cache of Review instances, keyed by primary key
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        # Property setters will validate
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return f"<Review {self.id}: {self.year} for Employee {self.employee_id}>"

    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INTEGER,
                summary TEXT,
                employee_id INTEGER,
                FOREIGN KEY(employee_id) REFERENCES employees(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        sql = "DROP TABLE IF EXISTS reviews;"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        if self.id is None:
            sql = """
                INSERT INTO reviews (year, summary, employee_id)
                VALUES (?, ?, ?)
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            CONN.commit()
            self.id = CURSOR.lastrowid
        else:
            sql = """
                UPDATE reviews
                SET year = ?, summary = ?, employee_id = ?
                WHERE id = ?
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
            CONN.commit()
        type(self).all[self.id] = self

    @classmethod
    def create(cls, year, summary, employee_id):
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        if row is None:
            return None
        rid, year, summary, emp_id = row
        existing = cls.all.get(rid)
        if existing:
            existing.year = year
            existing.summary = summary
            existing.employee_id = emp_id
            return existing
        review = cls(year, summary, emp_id, id=rid)
        cls.all[rid] = review
        return review

    @classmethod
    def find_by_id(cls, id):
        row = CURSOR.execute(
            "SELECT * FROM reviews WHERE id = ?", (id,)
        ).fetchone()
        return cls.instance_from_db(row)

    @classmethod
    def get_all(cls):
        rows = CURSOR.execute("SELECT * FROM reviews").fetchall()
        return [cls.instance_from_db(r) for r in rows]

    def update(self):
        sql = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """
        CURSOR.execute(
            sql,
            (self.year, self.summary, self.employee_id, self.id)
        )
        CONN.commit()
        type(self).all[self.id] = self

    def delete(self):
        CURSOR.execute("DELETE FROM reviews WHERE id = ?", (self.id,))
        CONN.commit()
        del type(self).all[self.id]
        self.id = None

    # --- Property validations ---
    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int) or value < 2000:
            raise ValueError("year must be an integer ≥ 2000")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("summary must be a non-empty string")
        self._summary = value

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        if not isinstance(value, int) or Employee.find_by_id(value) is None:
            raise ValueError("employee_id must refer to an existing Employee")
        self._employee_id = value
