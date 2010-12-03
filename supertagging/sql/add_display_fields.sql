
ALTER TABLE supertagging_supertag ADD COLUMN display_name character varying(150);
ALTER TABLE supertagging_supertag ADD COLUMN description text;
ALTER TABLE supertagging_supertag ADD COLUMN icon character varying(100);

CREATE TABLE supertagging_supertag_related
(
  id serial NOT NULL,
  from_supertag_id integer NOT NULL,
  to_supertag_id integer NOT NULL,
  CONSTRAINT supertagging_supertag_related_pkey PRIMARY KEY (id),
  CONSTRAINT supertagging_supertag_related_from_supertag_id_fkey FOREIGN KEY (from_supertag_id)
      REFERENCES supertagging_supertag (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT supertagging_supertag_related_to_supertag_id_fkey FOREIGN KEY (to_supertag_id)
      REFERENCES supertagging_supertag (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT supertagging_supertag_related_from_supertag_id_key UNIQUE (from_supertag_id, to_supertag_id)
)
WITH (OIDS=FALSE);