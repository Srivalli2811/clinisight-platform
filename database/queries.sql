USE clinsight;
SELECT COUNT(*) FROM patients;
SELECT COUNT(*) FROM appointments;
SELECT COUNT(*) FROM treatments;
SELECT COUNT(*) FROM bills;
SELECT COUNT(*) FROM rooms;

-- Query 1 — Get all patients with their appointment details
SELECT p.full_name, p.gender, a.appointment_date, a.status
FROM patients p
INNER JOIN appointments a ON p.patient_id = a.patient_id
LIMIT 10;

-- Query 2 — Get all patients even if they have no appointments:
SELECT p.full_name, a.appointment_date, a.status
FROM patients p
LEFT JOIN appointments a ON p.patient_id = a.patient_id
LIMIT 10;

-- Query 3 — Get patient name, doctor name, department for every appointment:
SELECT p.full_name AS patient, d.full_name AS doctor,
       dept.dept_name AS department, a.appointment_date, a.status
FROM appointments a
INNER JOIN patients p ON a.patient_id = p.patient_id
INNER JOIN doctors d ON a.doctor_id = d.doctor_id
INNER JOIN departments dept ON d.dept_id = dept.dept_id
LIMIT 10;

-- Query 4 — Total appointments per department:
SELECT dept.dept_name, COUNT(a.appointment_id) AS total_appointments
FROM appointments a
INNER JOIN doctors d ON a.doctor_id = d.doctor_id
INNER JOIN departments dept ON d.dept_id = dept.dept_id
GROUP BY dept.dept_name
ORDER BY total_appointments DESC;

-- Query 5 — Total revenue per department:
SELECT dept.dept_name, 
       ROUND(SUM(t.cost), 2) AS total_revenue
FROM treatments t
INNER JOIN appointments a ON t.appointment_id = a.appointment_id
INNER JOIN doctors d ON a.doctor_id = d.doctor_id
INNER JOIN departments dept ON d.dept_id = dept.dept_id
GROUP BY dept.dept_name
ORDER BY total_revenue DESC;

-- Query 6 — Top 5 doctors by number of completed appointments:
SELECT d.full_name, d.specialization,
       COUNT(a.appointment_id) AS completed_appointments
FROM appointments a
INNER JOIN doctors d ON a.doctor_id = d.doctor_id
WHERE a.status = 'Completed'
GROUP BY d.doctor_id, d.full_name, d.specialization
ORDER BY completed_appointments DESC
LIMIT 5;

-- Query 7 — Patients who have more than 3 appointments:
SELECT full_name, patient_id
FROM patients
WHERE patient_id IN (
    SELECT patient_id
    FROM appointments
    GROUP BY patient_id
    HAVING COUNT(*) > 3
);

-- Query 8 — Departments with above average appointments:
SELECT dept_name, total_appointments
FROM (
    SELECT dept.dept_name, COUNT(a.appointment_id) AS total_appointments
    FROM appointments a
    INNER JOIN doctors d ON a.doctor_id = d.doctor_id
    INNER JOIN departments dept ON d.dept_id = dept.dept_id
    GROUP BY dept.dept_name
) AS dept_stats
WHERE total_appointments > (
    SELECT AVG(total_appointments)
    FROM (
        SELECT COUNT(a.appointment_id) AS total_appointments
        FROM appointments a
        INNER JOIN doctors d ON a.doctor_id = d.doctor_id
        INNER JOIN departments dept ON d.dept_id = dept.dept_id
        GROUP BY dept.dept_name
    ) AS avg_stats
);

-- Query 9 — Monthly revenue trend:
WITH monthly_revenue AS (
    SELECT 
        DATE_FORMAT(a.appointment_date, '%Y-%m') AS month,
        ROUND(SUM(t.cost), 2) AS revenue
    FROM treatments t
    INNER JOIN appointments a ON t.appointment_id = a.appointment_id
    GROUP BY DATE_FORMAT(a.appointment_date, '%Y-%m')
)
SELECT month, revenue
FROM monthly_revenue
ORDER BY month;

-- Query 10 — Patients with pending bills and their total unpaid amount:
WITH unpaid_bills AS (
    SELECT patient_id,
           ROUND(SUM(total_amount - paid_amount), 2) AS unpaid_amount
    FROM bills
    WHERE payment_status IN ('Pending', 'Partial')
    GROUP BY patient_id
)
SELECT p.full_name, u.unpaid_amount
FROM unpaid_bills u
INNER JOIN patients p ON u.patient_id = p.patient_id
ORDER BY u.unpaid_amount DESC
LIMIT 10;

-- Query 11 — Rank doctors by revenue generated:
SELECT 
    d.full_name,
    dept.dept_name,
    ROUND(SUM(t.cost), 2) AS total_revenue,
    RANK() OVER (ORDER BY SUM(t.cost) DESC) AS revenue_rank
FROM treatments t
INNER JOIN appointments a ON t.appointment_id = a.appointment_id
INNER JOIN doctors d ON a.doctor_id = d.doctor_id
INNER JOIN departments dept ON d.dept_id = dept.dept_id
GROUP BY d.doctor_id, d.full_name, dept.dept_name;

-- Query 12 — Rank doctors within each department by appointments:
SELECT 
    d.full_name,
    dept.dept_name,
    COUNT(a.appointment_id) AS total_appointments,
    RANK() OVER (PARTITION BY dept.dept_name ORDER BY COUNT(a.appointment_id) DESC) AS dept_rank
FROM appointments a
INNER JOIN doctors d ON a.doctor_id = d.doctor_id
INNER JOIN departments dept ON d.dept_id = dept.dept_id
GROUP BY d.doctor_id, d.full_name, dept.dept_name;

-- Query 13 — Running total of revenue month by month:
WITH monthly AS (
    SELECT 
        DATE_FORMAT(a.appointment_date, '%Y-%m') AS month,
        ROUND(SUM(t.cost), 2) AS revenue
    FROM treatments t
    INNER JOIN appointments a ON t.appointment_id = a.appointment_id
    GROUP BY DATE_FORMAT(a.appointment_date, '%Y-%m')
)
SELECT 
    month,
    revenue,
    ROUND(SUM(revenue) OVER (ORDER BY month), 2) AS running_total
FROM monthly
ORDER BY month;

