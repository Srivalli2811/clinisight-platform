DELIMITER //

CREATE PROCEDURE GetBillingSummary()
BEGIN
    SELECT 
        payment_status,
        COUNT(*) AS total_bills,
        ROUND(SUM(total_amount), 2) AS total_billed,
        ROUND(SUM(paid_amount), 2) AS total_collected,
        -- outstanding = total owed minus what's been paid
        ROUND(SUM(total_amount - paid_amount), 2) AS total_outstanding
    FROM bills
    GROUP BY payment_status;
END //

DELIMITER ;