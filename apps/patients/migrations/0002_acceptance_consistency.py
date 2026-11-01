from django.db import migrations

FORWARD = """
CREATE FUNCTION nakre_validate_acceptance() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE request_key uuid; request_status text; has_case boolean;
BEGIN
    IF TG_TABLE_NAME = 'intake_carerequest' THEN
        request_key := COALESCE(NEW.id, OLD.id);
    ELSE
        IF TG_OP = 'UPDATE' AND OLD.request_id <> NEW.request_id THEN
            RAISE EXCEPTION 'Case source cannot change' USING ERRCODE = '23514';
        END IF;
        request_key := COALESCE(NEW.request_id, OLD.request_id);
    END IF;
    SELECT status INTO request_status FROM intake_carerequest WHERE id = request_key FOR UPDATE;
    IF NOT FOUND THEN RETURN NULL; END IF;
    SELECT EXISTS(SELECT 1 FROM patients_patientcase WHERE request_id = request_key) INTO has_case;
    IF (request_status = 'accepted') <> has_case THEN
        RAISE EXCEPTION 'Acceptance and case must be committed together' USING ERRCODE = '23514';
    END IF;
    RETURN NULL;
END;
$$;
CREATE CONSTRAINT TRIGGER nakre_request_case_consistency AFTER INSERT OR UPDATE ON intake_carerequest
DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION nakre_validate_acceptance();
CREATE CONSTRAINT TRIGGER nakre_case_request_consistency AFTER INSERT OR UPDATE OR DELETE ON patients_patientcase
DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION nakre_validate_acceptance();
"""
REVERSE = """
DROP TRIGGER nakre_case_request_consistency ON patients_patientcase;
DROP TRIGGER nakre_request_case_consistency ON intake_carerequest;
DROP FUNCTION nakre_validate_acceptance();
"""


class Migration(migrations.Migration):
    dependencies = [("patients", "0001_initial"), ("intake", "0002_confirmed_services")]
    operations = [migrations.RunSQL(FORWARD, REVERSE)]
