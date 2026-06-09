from django.db import migrations


def populate_quartiers(apps, schema_editor):
    Quartier = apps.get_model('quartiers', 'Quartier')
    quartiers = [
        'Adidogomé', 'Agoè', 'Bè', 'Tokoin', 'Attiégou',
        'Kodjoviakopé', 'Amoutivé', 'Doumasséssé', 'Hanoukopé', 'Sylvanus',
    ]
    for nom in quartiers:
        Quartier.objects.get_or_create(nom=nom)


class Migration(migrations.Migration):

    dependencies = [
        ('quartiers', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_quartiers, migrations.RunPython.noop),
    ]
