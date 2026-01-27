-- 02_seed_data_mysql.sql
-- Setter inn: studiesteder, studieformer, studieprogram og studietilbud

USE fagskolen;

START TRANSACTION;

-- 1) STUDIESTEDER
INSERT IGNORE INTO studiesteder (navn) VALUES
  ('Fredrikstad'),
  ('Kjeller'),
  ('Drammen'),
  ('Kongsberg'),
  ('Gauldal');

-- 2) STUDIEFORMER
INSERT IGNORE INTO studieformer (navn) VALUES
  ('Samlingsbasert'),
  ('Nettbasert med samlinger'),
  ('Modulbasert'),
  ('Deltid');

-- 3) STUDIEPROGRAM (4 programmer fra listen din)
INSERT IGNORE INTO studieprogram (navn, kategori, program_url, kort_beskrivelse) VALUES
  (
    'Observasjons- og vurderingskompetanse i helsetjenesten',
    'Helse',
    'https://fagskolen-viken.no/studier/helse/observasjons-og-vurderingskompetanse-i-helsetjenesten',
    'Videreutdanning med fokus på systematisk observasjon, vurdering og dokumentasjon av helsetilstand.'
  ),
  (
    'Optometri for medhjelpere',
    'Helse',
    'https://fagskolen-viken.no/studier/helse/optometri-medhjelpere',
    'Videreutdanning for medhjelpere innen optometri/optisk virksomhet.'
  ),
  (
    'Praktisk veiledning',
    'Helse',
    'https://fagskolen-viken.no/studier/helse/praktisk-veiledning',
    'Videreutdanning som styrker kompetanse i veiledning, kommunikasjon og etisk refleksjon i helsetjenesten.'
  ),
  (
    'Psykisk helsearbeid og rusarbeid',
    'Helse',
    'https://fagskolen-viken.no/studier/helse/psykisk-helsearbeid-og-rusarbeid',
    'Utdanning rettet mot arbeid med psykisk helse og rus, med nettundervisning kombinert med fysiske samlinger.'
  );

-- 4) STUDIETILBUD
-- 4.1 Observasjons- og vurderingskompetanse i helsetjenesten
INSERT IGNORE INTO studietilbud (
  studieprogram_id, studiested_id, studieform_id,
  varighet_verdi, varighet_enhet, studiepoeng_min, studiepoeng_max,
  apent_for_opptak, merknad
)
SELECT
  sp.studieprogram_id,
  ss.studiested_id,
  sf.studieform_id,
  2, 'år', 60, 60,
  1,
  'Lang variant (2 år).'
FROM studieprogram sp
JOIN studiesteder ss ON ss.navn IN ('Fredrikstad','Kjeller','Drammen')
JOIN studieformer sf ON sf.navn = 'Nettbasert med samlinger'
WHERE sp.navn = 'Observasjons- og vurderingskompetanse i helsetjenesten';

INSERT IGNORE INTO studietilbud (
  studieprogram_id, studiested_id, studieform_id,
  varighet_verdi, varighet_enhet, studiepoeng_min, studiepoeng_max,
  apent_for_opptak, merknad
)
SELECT
  sp.studieprogram_id,
  ss.studiested_id,
  sf.studieform_id,
  12, 'uker', 10, 60,
  1,
  'Kort variant (ca. 12 uker). Studiepoeng kan variere.'
FROM studieprogram sp
JOIN studiesteder ss ON ss.navn IN ('Fredrikstad','Kongsberg','Gauldal')
JOIN studieformer sf ON sf.navn = 'Samlingsbasert'
WHERE sp.navn = 'Observasjons- og vurderingskompetanse i helsetjenesten';

-- 4.2 Optometri for medhjelpere
INSERT IGNORE INTO studietilbud (
  studieprogram_id, studiested_id, studieform_id,
  varighet_verdi, varighet_enhet, studiepoeng_min, studiepoeng_max,
  apent_for_opptak, merknad
)
SELECT
  sp.studieprogram_id,
  ss.studiested_id,
  sf.studieform_id,
  1, 'år', 30, 30,
  1,
  'Kongsberg (1 år).'
FROM studieprogram sp
JOIN studiesteder ss ON ss.navn = 'Kongsberg'
JOIN studieformer sf ON sf.navn = 'Samlingsbasert'
WHERE sp.navn = 'Optometri for medhjelpere';

-- 4.3 Praktisk veiledning
INSERT IGNORE INTO studietilbud (
  studieprogram_id, studiested_id, studieform_id,
  varighet_verdi, varighet_enhet, studiepoeng_min, studiepoeng_max,
  apent_for_opptak, merknad
)
SELECT
  sp.studieprogram_id,
  ss.studiested_id,
  sf.studieform_id,
  1, 'år', 25, 30,
  1,
  '1 år. Studiepoeng kan variere mellom 25 og 30.'
FROM studieprogram sp
JOIN studiesteder ss ON ss.navn IN ('Kongsberg','Fredrikstad','Kjeller')
JOIN studieformer sf ON sf.navn = 'Samlingsbasert'
WHERE sp.navn = 'Praktisk veiledning';

-- 4.4 Psykisk helsearbeid og rusarbeid
INSERT IGNORE INTO studietilbud (
  studieprogram_id, studiested_id, studieform_id,
  varighet_verdi, varighet_enhet, studiepoeng_min, studiepoeng_max,
  apent_for_opptak, merknad
)
SELECT
  sp.studieprogram_id,
  ss.studiested_id,
  sf.studieform_id,
  2, 'år', 60, 60,
  1,
  'Nettundervisning kombinert med fysiske samlinger.'
FROM studieprogram sp
JOIN studiesteder ss ON ss.navn IN ('Fredrikstad','Kjeller','Kongsberg')
JOIN studieformer sf ON sf.navn = 'Nettbasert med samlinger'
WHERE sp.navn = 'Psykisk helsearbeid og rusarbeid';

COMMIT;
