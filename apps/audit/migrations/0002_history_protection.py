from django.db import migrations

TABLES = [
    "audit_auditevent",
    "intake_consentrecord",
    "intake_requestreview",
    "interventions_interventionevent",
    "notifications_notificationattempt",
]
FORWARD = """
CREATE FUNCTION nakre_reject_history_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'History records are append-only; use the approved retention procedure' USING ERRCODE = '23514';
END;
$$;
""" + "\n".join(
    f"CREATE TRIGGER nakre_immutable BEFORE UPDATE OR DELETE ON {table} FOR EACH ROW EXECUTE FUNCTION nakre_reject_history_mutation();"
    for table in TABLES
)
REVERSE = (
    "\n".join(f"DROP TRIGGER nakre_immutable ON {table};" for table in TABLES)
    + "\nDROP FUNCTION nakre_reject_history_mutation();"
)


class Migration(migrations.Migration):
    dependencies = [
        ("audit", "0001_initial"),
        ("intake", "0002_confirmed_services"),
        ("interventions", "0001_initial"),
        ("notifications", "0001_initial"),
    ]
    operations = [migrations.RunSQL(FORWARD, REVERSE)]
