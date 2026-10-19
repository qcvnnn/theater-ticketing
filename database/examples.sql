-- Read-only examples for the PORTFOLIO schema. Counts are retained active tickets,
-- not historical gross sales or proof of attendance. No price/payment data exists.

-- 1. Upcoming shows: one row per show.
SELECT s."ID_ShowDetails", p."Title", th."Title" AS theater,
       s."Show_Date",s."Start_time"
FROM "Show_Details" s JOIN "Productions" p USING ("ID_Production")
JOIN "Theaters" th USING ("ID_Theater")
WHERE s."Show_Date"+s."Start_time">LOCALTIMESTAMP
ORDER BY s."Show_Date",s."Start_time";

-- 2. Available seats: one row per show and seat category.
SELECT "ShowDetails_ID","SeatType","TotalSeats","SoldSeats",
       "TotalSeats"-"SoldSeats" AS available
FROM "ShowSeats" ORDER BY "ShowDetails_ID","SeatType";

-- 3. Viewer ticket history. Replace the demo login with a bound parameter in an app.
SELECT t."ID_Ticket",p."Title",s."Show_Date",s."Start_time",t."SeatType",t."Status"
FROM "Tickets" t JOIN "Clients" c USING ("ID_Client")
JOIN "Show_Details" s USING ("ID_ShowDetails") JOIN "Productions" p USING ("ID_Production")
WHERE c."Login"='demo' ORDER BY t."CreatedAt" DESC;

-- 4. Occupancy. Aggregate capacities before joining any ticket-level data.
SELECT "ShowDetails_ID",sum("TotalSeats") AS capacity,sum("SoldSeats") AS issued,
 round(100.0*sum("SoldSeats")/NULLIF(sum("TotalSeats"),0),2) AS occupancy_pct
FROM "ShowSeats" GROUP BY "ShowDetails_ID" ORDER BY occupancy_pct DESC NULLS LAST;

-- 5. Popular productions by retained tickets (cancelled tickets excluded).
SELECT p."ID_Production",p."Title",count(t."ID_Ticket") AS active_tickets
FROM "Productions" p LEFT JOIN "Show_Details" s USING ("ID_Production")
LEFT JOIN "Tickets" t ON t."ID_ShowDetails"=s."ID_ShowDetails" AND t."Status"='active'
GROUP BY p."ID_Production",p."Title" ORDER BY active_tickets DESC,p."Title";

-- 6. Average review rating. No ticket join: otherwise reviews would be multiplied.
SELECT p."ID_Production",p."Title",count(r."ID_Review") AS reviews,
 round(avg(r."Assessment"),2) AS average_rating
FROM "Productions" p LEFT JOIN "Reviews" r ON r."ID_Productions"=p."ID_Production"
GROUP BY p."ID_Production",p."Title" ORDER BY average_rating DESC NULLS LAST;

-- 7. Shows without active tickets, including those with only cancelled tickets.
SELECT s."ID_ShowDetails",s."Show_Date",p."Title"
FROM "Show_Details" s JOIN "Productions" p USING ("ID_Production")
WHERE NOT EXISTS (SELECT 1 FROM "Tickets" t WHERE t."ID_ShowDetails"=s."ID_ShowDetails" AND t."Status"='active');

-- Diagnostic: should return zero rows. Direct manual counter edits are unsupported.
SELECT ss."ShowDetails_ID",ss."SeatType",ss."SoldSeats",count(t."ID_Ticket") AS actual
FROM "ShowSeats" ss LEFT JOIN "Tickets" t ON t."ID_ShowDetails"=ss."ShowDetails_ID"
 AND t."SeatType"=ss."SeatType" AND t."Status"='active'
GROUP BY ss."ID_ShowSeat" HAVING ss."SoldSeats"<>count(t."ID_Ticket");
