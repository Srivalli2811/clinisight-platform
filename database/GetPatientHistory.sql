DELIMITER //

CREATE PROCEDURE GetPatientHistory(IN p_id INT)
-- IN means this is an input parameter we pass when calling
-- p_id is the patient ID we want history for
BEGIN
    SELECT 
        p.full_name AS patient,         -- patient name
        a.appointment_date,             -- when they visited
        a.status,                       -- completed/scheduled/cancelled
        d.full_name AS doctor,          -- which doctor they saw
        dept.dept_name AS department,   -- which department
        t.treatment_name,               -- what treatment they received
        t.cost                          -- how much it cost
    FROM patients p
    -- LEFT JOIN because patient may have appointments with no treatments yet
    LEFT JOIN appointments a ON p.patient_id = a.patient_id
    LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
    LEFT JOIN departments dept ON d.dept_id = dept.dept_id
    LEFT JOIN treatments t ON a.appointment_id = t.appointment_id
    -- filter by the patient ID we passed in when calling
    WHERE p.patient_id = p_id;
END //

DELIMITER ;