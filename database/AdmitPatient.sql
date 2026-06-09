DELIMITER //

CREATE PROCEDURE AdmitPatient(
    IN p_name VARCHAR(100),
    IN p_dob DATE,
    IN p_gender ENUM('Male', 'Female', 'Other'),
    IN p_phone VARCHAR(15),
    IN p_doctor_id INT,
    IN p_room_number VARCHAR(10)
)
BEGIN
    -- Variable to store the new patient's auto-generated ID
    -- We need this to link appointments and bills to this specific patient
    DECLARE new_patient_id INT;

    -- Safety net — if ANY error occurs anywhere below
    -- automatically undo everything and show error message
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'Something went wrong. All changes undone.' AS message;
    END;

    -- Nothing below is saved until COMMIT
    START TRANSACTION;

    -- Step 1: Create the patient record
    INSERT INTO patients(full_name, dob, gender, phone)
    VALUES(p_name, p_dob, p_gender, p_phone);

    -- Get the auto-generated patient_id of the patient we just inserted
    -- LAST_INSERT_ID() always gives the ID of the most recent INSERT
    SET new_patient_id = LAST_INSERT_ID();

    -- Step 2: Create their first appointment
    -- NOW() gives current datetime, CURDATE() gives current date
    INSERT INTO appointments(patient_id, doctor_id, appointment_date, status)
    VALUES(new_patient_id, p_doctor_id, NOW(), 'Scheduled');

    -- Step 3: Assign the room
    -- AND is_occupied = FALSE is a safety check
    -- Only assigns if room is truly empty — prevents double booking
    UPDATE rooms 
    SET is_occupied = TRUE, patient_id = new_patient_id
    WHERE room_number = p_room_number AND is_occupied = FALSE;

    -- Step 4: Create initial bill with zero amount
    -- Amount will be updated as treatments are added
    INSERT INTO bills(patient_id, total_amount, paid_amount, payment_status, bill_date)
    VALUES(new_patient_id, 0, 0, 'Pending', CURDATE());

    -- All 4 steps succeeded — now save everything permanently
    COMMIT;
    SELECT 'Patient admitted successfully!' AS message,
           new_patient_id AS patient_id;
END //

DELIMITER ;