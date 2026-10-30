-- SQLite queries. Dates are ISO YYYY-MM-DD strings; counts use one row per appointment.
-- Each statement is executed and exported by python/run_analysis.py.
-- 01 Annual KPIs: cancelled bookings are excluded from the no-show denominator.
SELECT COUNT(*) AS bookings,
 SUM(CASE WHEN status='Attended' THEN 1 ELSE 0 END) AS attended,
 SUM(CASE WHEN status='No-show' THEN 1 ELSE 0 END) AS no_shows,
 SUM(CASE WHEN status='Cancelled' THEN 1 ELSE 0 END) AS cancelled,
 1.0*SUM(CASE WHEN status='No-show' THEN 1 ELSE 0 END)/NULLIF(SUM(CASE WHEN status IN ('Attended','No-show') THEN 1 ELSE 0 END),0) AS no_show_rate,
 AVG(CASE WHEN status='Attended' THEN wait_minutes END) AS avg_wait_minutes
FROM appointments;
-- 02 Monthly performance, conditional aggregation.
SELECT substr(appointment_date,1,7) AS month, COUNT(*) AS bookings,
 SUM(CASE WHEN status='Attended' THEN 1 ELSE 0 END) AS attended,
 SUM(CASE WHEN status='No-show' THEN 1 ELSE 0 END) AS no_shows,
 1.0*SUM(CASE WHEN status='No-show' THEN 1 ELSE 0 END)/NULLIF(SUM(CASE WHEN status IN ('Attended','No-show') THEN 1 ELSE 0 END),0) AS no_show_rate,
 AVG(CASE WHEN status='Attended' THEN wait_minutes END) AS avg_wait_minutes
FROM appointments GROUP BY 1 ORDER BY 1;
-- 03 Join department targets and calculate attended-only wait performance.
SELECT d.department,COUNT(*) AS bookings,
 SUM(CASE WHEN a.status='Attended' THEN 1 ELSE 0 END) AS attended,
 AVG(CASE WHEN a.status='Attended' THEN a.wait_minutes END) AS avg_wait_minutes,
 1.0*SUM(CASE WHEN a.status='Attended' AND a.wait_minutes<=d.wait_target_minutes THEN 1 ELSE 0 END)/NULLIF(SUM(CASE WHEN a.status='Attended' THEN 1 ELSE 0 END),0) AS within_target_rate
FROM appointments a JOIN departments d ON a.department_id=d.department_id GROUP BY d.department ORDER BY avg_wait_minutes DESC;
-- 04 Booking lead-time bands. Boundaries are mutually exclusive.
WITH base AS (SELECT *,CAST(julianday(appointment_date)-julianday(booking_date) AS INTEGER) AS lead_days FROM appointments),
bands AS (SELECT *,CASE WHEN lead_days<=7 THEN '01 0-7 days' WHEN lead_days<=21 THEN '02 8-21 days' ELSE '03 22+ days' END AS lead_band FROM base)
SELECT lead_band,COUNT(*) AS bookings,SUM(CASE WHEN status='No-show' THEN 1 ELSE 0 END) AS no_shows,
1.0*SUM(CASE WHEN status='No-show' THEN 1 ELSE 0 END)/NULLIF(SUM(CASE WHEN status IN ('Attended','No-show') THEN 1 ELSE 0 END),0) AS no_show_rate
FROM bands GROUP BY lead_band ORDER BY lead_band;
-- 05 Reminder association, not a causal effect estimate.
SELECT reminder_sent,COUNT(*) AS bookings,
1.0*SUM(CASE WHEN status='No-show' THEN 1 ELSE 0 END)/NULLIF(SUM(CASE WHEN status IN ('Attended','No-show') THEN 1 ELSE 0 END),0) AS no_show_rate
FROM appointments GROUP BY reminder_sent ORDER BY reminder_sent;
-- 06 Month-over-month bookings with a window function.
WITH m AS (SELECT substr(appointment_date,1,7) AS month,COUNT(*) AS bookings FROM appointments GROUP BY 1)
SELECT month,bookings,LAG(bookings) OVER (ORDER BY month) AS previous_bookings,
1.0*(bookings-LAG(bookings) OVER (ORDER BY month))/NULLIF(LAG(bookings) OVER (ORDER BY month),0) AS mom_growth
FROM m ORDER BY month;
