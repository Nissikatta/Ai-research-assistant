-- =============================================================================
-- Question 2: Rfam MySQL Database Queries
-- =============================================================================
-- Database: Rfam (Public MySQL instance: mysql-rfam-public.ebi.ac.uk:4497)
-- Relevant tables: family, rfamseq, full_region, taxonomy, clan, clan_membership
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Query A: Determine how many types of Acacia plants are present in the taxonomy table.
-- Returns the count with a clearly named column.
-- -----------------------------------------------------------------------------
SELECT 
    COUNT(*) AS acacia_types_count
FROM 
    taxonomy
WHERE 
    species LIKE '%Acacia%' 
    OR tax_string LIKE '%Acacia%';


-- -----------------------------------------------------------------------------
-- Query B: Determine which type of wheat has the longest DNA sequence.
-- Uses the rfamseq and taxonomy tables to find the wheat type (genus Triticum)
-- with the maximum sequence length.
-- Returns the relevant wheat species/type and its DNA sequence length.
-- -----------------------------------------------------------------------------
SELECT 
    t.species AS wheat_type,
    r.length AS max_dna_sequence_length
FROM 
    rfamseq r
JOIN 
    taxonomy t ON r.ncbi_id = t.ncbi_id
WHERE 
    t.species LIKE '%Triticum%' 
    OR t.tax_string LIKE '%Triticum%'
    OR t.species LIKE '%wheat%'
ORDER BY 
    r.length DESC
LIMIT 1;


-- -----------------------------------------------------------------------------
-- Query C: Generate a list containing family accession, family name, and maximum 
-- DNA sequence length for families where the maximum sequence length > 1,000,000.
-- 
-- Requirements:
-- - Sorted by max DNA sequence length in descending order.
-- - 15 results per page.
-- - Returns Page 9 of results (results 121 to 135 -> LIMIT 15 OFFSET 120).
-- -----------------------------------------------------------------------------
SELECT 
    f.rfam_acc AS family_accession,
    f.rfam_id AS family_name,
    MAX(r.length) AS max_dna_sequence_length
FROM 
    family f
JOIN 
    full_region fr ON f.rfam_acc = fr.rfam_acc
JOIN 
    rfamseq r ON fr.rfamseq_acc = r.rfamseq_acc
GROUP BY 
    f.rfam_acc, 
    f.rfam_id
HAVING 
    MAX(r.length) > 1000000
ORDER BY 
    max_dna_sequence_length DESC
LIMIT 15 OFFSET 120;
