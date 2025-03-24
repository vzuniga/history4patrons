SELECT
brp.best_title AS "Title",
brp.best_author AS "Author",
id2reckey(rh.item_record_metadata_id) || 'a'  AS "Item Number",
TO_CHAR (rh.checkout_gmt::DATE, 'MM/DD/YYYY') AS "Checkedout Date"
FROM reading_history rh
LEFT JOIN bib_record_property brp
on rh.bib_record_metadata_id = brp.bib_record_id
-- Replace the placeholder pnumber for an actual patron record number.
WHERE id2reckey(rh.patron_record_metadata_id) || 'a' = 'p9999999a'
ORDER BY rh.checkout_gmt DESC 