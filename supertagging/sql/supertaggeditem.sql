CREATE INDEX st_sti_generic_relation_key
   ON supertagging_supertaggeditem (object_id, content_type_id);

CREATE INDEX st_sti_tagid_objid_contentid_relevance_key
  ON supertagging_supertaggeditem (tag_id, object_id, content_type_id, relevance);