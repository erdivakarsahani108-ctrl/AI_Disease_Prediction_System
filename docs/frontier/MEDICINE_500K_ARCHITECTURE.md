# 500,000-Medicine Catalog Architecture

Do NOT fill the catalog with invented medicines. The target is capacity for at least 500,000 verified records.

Medical systems may include, subject to verified source coverage:
- Allopathic/conventional
- Ayurvedic
- Homeopathic
- Unani
- Siddha
- Naturopathy
- Traditional systems where legally appropriate
- OTC products
- Prescription products
- Hospital products
- Medical devices and diagnostics as a separate entity type

Each record should support:
medicine_id, generic_name, brand_name, manufacturer, system, dosage_form,
strength, route, active_ingredients, inactive_ingredients, indications,
contraindications, warnings, adverse_effects, interactions, allergy_risks,
age_restrictions, pregnancy_lactation_status, renal_hepatic_notes,
storage, prescription_status, country, regulator, registration_number,
source, source_version, effective_date, expiry/review_date, evidence_level,
barcode/GTIN where available, pharmacologic_class, therapeutic_class,
synonyms, multilingual_names, provenance_hash.

For biopsy/pathology:
biopsy is a diagnostic procedure/result domain, not a medicine attribute.
Create separate pathology_report, specimen, finding, diagnosis_candidate,
image_asset and evidence entities.

For symptoms:
Use a controlled vocabulary and map synonyms/translations to canonical IDs.
Never infer a medication recommendation solely from a symptom.

For brands:
Brand availability varies by country and time. Store jurisdiction and effective dates.
