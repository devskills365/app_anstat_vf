/* Pour créer des partition */
use annuaire;
ALTER TABLE v1_indicateur ADD COLUMN cle_dimension VARCHAR(255);
SET SQL_SAFE_UPDATES = 0;
UPDATE v1_indicateur SET cle_dimension = REPLACE(REPLACE(Dimension, ' ', '-'), '/', '-');
UPDATE v1_indicateur SET cle_dimension = REPLACE(cle_dimension, '---', '-');
SELECT distinct cle_dimension FROM v1_indicateur;
SET SQL_SAFE_UPDATES = 1;