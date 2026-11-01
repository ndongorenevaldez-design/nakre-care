from django.db import migrations


def seed(apps, schema_editor):
    ServiceType = apps.get_model("intake", "ServiceType")
    for code, label in [
        ("domicile", "Accompagnement à domicile"),
        ("hospitalier", "Accompagnement en milieu hospitalier"),
        ("deplacements", "Rendez-vous et déplacements utiles"),
    ]:
        ServiceType.objects.get_or_create(code=code, defaults={"label": label})


class Migration(migrations.Migration):
    dependencies = [("intake", "0001_initial")]
    # Preserve referenced catalogue data when reversing; no destructive seed rollback.
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
