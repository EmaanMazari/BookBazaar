# Generated data migration to populate comprehensive Pakistani exhibition seed data
from django.db import migrations


def populate_exhibition_data(apps, schema_editor):
    try:
        from bazaar.services.seed_service import ensure_demo_listings
        ensure_demo_listings(force=True)
    except Exception as e:
        print(f"Warning: Failed to run exhibition seed data during migration: {e}")


class Migration(migrations.Migration):

    dependencies = [
        ('bazaar', '0009_alter_platformsetting_platform_name_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_exhibition_data, reverse_code=migrations.RunPython.noop),
    ]
