DELIMITER //

CREATE PROCEDURE GetDepartmentRevenue()
-- No input needed — returns all departments
BEGIN
    SELECT 
        dept.dept_name,
        -- DISTINCT prevents counting same appointment multiple times
        -- when one appointment has multiple treatments
        COUNT(DISTINCT a.appointment_id) AS total_appointments,
        COUNT(DISTINCT a.patient_id) AS unique_patients,
        ROUND(SUM(t.cost), 2) AS total_revenue,
        ROUND(AVG(t.cost), 2) AS avg_treatment_cost
    FROM departments dept
    LEFT JOIN doctors d ON dept.dept_id = d.dept_id
    LEFT JOIN appointments a ON d.doctor_id = a.doctor_id
    LEFT JOIN treatments t ON a.appointment_id = t.appointment_id
    GROUP BY dept.dept_name
    -- Highest revenue department appears first
    ORDER BY total_revenue DESC;
END //

DELIMITER ;