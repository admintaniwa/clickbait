DROP TABLE IF EXISTS cb_titulares;
CREATE TABLE cb_titulares (
  id             SERIAL       NOT NULL,
  titulo         TEXT         NOT NULL,
  fuente         VARCHAR(88)  NOT NULL,
  cb			 VARCHAR(3)	  NOT NULL, check (cb in ('NO', 'SI')),
  score          NUMERIC      NOT NULL, check (score BETWEEN 0.0 AND 1.0),
  fec_creacion   TIMESTAMP     NOT NULL DEFAULT NOW(),
  CONSTRAINT cb_titulares_pk PRIMARY KEY (id)
);
CREATE INDEX idx_cb_titulares_fuente ON cb_titulares (fuente);

CREATE or REPLACE VIEW cb_view_agregados as
select to_char(fec_creacion,'YYYY-MM-DD') fecha,  fuente, count(*) num, 100.0 * sum(case when cb='SI' then 1.0  else 0 end) / count(*) clickbait_prc
from cb_titulares ct 
group by fecha, fuente 
having count(*) > 20 
order by 1,2;

-- Borrado de duplicados
DELETE FROM
cb_titulares a
USING cb_titulares b
WHERE a.id > b.id
AND a.titulo = b.titulo
and a.fuente = b.fuente;