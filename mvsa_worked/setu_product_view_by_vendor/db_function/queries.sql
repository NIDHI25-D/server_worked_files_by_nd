
DO

$do$

BEGIN

   IF NOT EXISTS (

      SELECT * FROM pg_roles WHERE rolname = 'odoo14_datastudio') THEN

      CREATE ROLE odoo14_datastudio LOGIN PASSWORD 'MVsa1!2@3#4$5%6^7&8*9(10)/*+-rj';

   END IF;

END

$do$;
