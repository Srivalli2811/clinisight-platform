-- appointments table
-- patient_id: used in every patient history query → GET /patients/{id}
-- doctor_id: used in every doctor analytics query → GET /doctors/{id}/appointments  
-- appointment_date: used for date range filtering in dashboard
-- status: used for filtering Completed/Scheduled/Cancelled appointments
CREATE INDEX idx_apt_patient ON appointments(patient_id);
CREATE INDEX idx_apt_doctor ON appointments(doctor_id);
CREATE INDEX idx_apt_date ON appointments(appointment_date);
CREATE INDEX idx_apt_status ON appointments(status);

-- treatments table
-- appointment_id: always joined with appointments table → GET /analytics/revenue
CREATE INDEX idx_treat_apt ON treatments(appointment_id);

-- bills table
-- patient_id: used in billing queries → GET /patients/{id}/bills
-- payment_status: used in billing dashboard → GET /analytics/billing
CREATE INDEX idx_bill_patient ON bills(patient_id);
CREATE INDEX idx_bill_status ON bills(payment_status);

-- doctors table
-- dept_id: always joined with departments → GET /departments/{id}/doctors
CREATE INDEX idx_doc_dept ON doctors(dept_id);




SHOW INDEX FROM appointments;
SHOW INDEX FROM treatments;
SHOW INDEX FROM bills;
SHOW INDEX FROM doctors;