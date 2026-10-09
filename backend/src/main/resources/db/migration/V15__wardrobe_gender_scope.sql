-- Match the gender rules already used by the AI catalog; keep existing items and asset metadata for saved looks.
ALTER TABLE wardrobe_items ADD COLUMN gender_scope VARCHAR(6) NOT NULL DEFAULT 'unisex';
ALTER TABLE wardrobe_items ADD CONSTRAINT wardrobe_gender_scope_check CHECK (gender_scope IN ('male','female','unisex'));
UPDATE wardrobe_items SET gender_scope='female' WHERE category='accessories' AND item_key IN ('bong-tai','hoa-cai-toc','khan-mo-qua','kieng-bac','non-quai-thao','vong-tay');
UPDATE wardrobe_items SET gender_scope='male' WHERE category='accessories' AND item_key IN ('khan-xep');
UPDATE wardrobe_items SET gender_scope='female' WHERE category='outfits' AND item_key IN ('nhat-binh','tu-than');
UPDATE wardrobe_items SET gender_scope='female' WHERE category='pants' AND item_key IN ('long-black','shorts-denim','skirt-long-ivory','skirt-short-navy');
UPDATE wardrobe_items SET gender_scope='male' WHERE category='pants' AND item_key IN ('cropped-olive','long-navy','shorts-khaki','slim-black','wide-charcoal');
UPDATE wardrobe_items SET gender_scope='female' WHERE category='shoes' AND item_key IN ('flats','giay-bup-be');
UPDATE wardrobe_items SET gender_scope='male' WHERE category='shoes' AND item_key IN ('giay-ta','loafers');
