-- SQLite compatible view
CREATE VIEW v_absences AS
WITH RECURSIVE split_periods AS (
    SELECT 
        abs.id,
        abs.object_id,
        g.id AS group_id,
        o.user_id,
        abs.type_id,
        abs.abs_date_start,
        MIN(abs.abs_date_end, DATE(abs.abs_date_start, 'start of month', '+1 month', '-1 day')) AS abs_date_end,
        abs.description,
        at.color AS at_color,
        at.name AS at_name
    FROM 
        absences abs
    LEFT JOIN 
        absence_types at ON abs.type_id = at.id
    LEFT JOIN 
        objects o ON abs.object_id = o.id
    LEFT JOIN 
        groups g ON o.group_id = g.id
    UNION ALL
    SELECT 
        sp.id,
        sp.object_id,
        sp.group_id,
        sp.user_id,
        sp.type_id,
        DATE(sp.abs_date_end, '+1 day') AS abs_date_start,
        MIN(abs.abs_date_end, DATE(DATE(sp.abs_date_end, '+1 day'), 'start of month', '+1 month', '-1 day')) AS abs_date_end,
        sp.description,
        sp.at_color,
        sp.at_name
    FROM 
        split_periods sp
    JOIN 
        absences abs ON sp.id = abs.id
    WHERE 
        sp.abs_date_end < abs.abs_date_end
)
SELECT
	*,
    CAST(julianday(abs_date_end) - julianday(abs_date_start) + 1 AS INTEGER) AS duration
FROM split_periods;