from django.db import migrations


def populate_categories(apps, schema_editor):
    Categorie = apps.get_model('categories', 'Categorie')
    SousCategorie = apps.get_model('categories', 'SousCategorie')

    categories_data = {
        'Services domestiques': ['Ménage', 'Lessive', 'Cuisine'],
        'Transport': ['Livraison', 'Courses'],
        'Travaux manuels': ['Jardinage', 'Maçonnerie', 'Électricité', 'Peinture'],
        'Assistance': ['Soutien scolaire', 'Informatique', 'Secrétariat'],
        'Évènementiel': ['Serveur', 'Accueil', 'Sécurité'],
    }

    for cat_nom, sous_cats in categories_data.items():
        categorie, _ = Categorie.objects.get_or_create(nom=cat_nom)
        for sc_nom in sous_cats:
            SousCategorie.objects.get_or_create(nom=sc_nom, categorie=categorie)


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_categories, migrations.RunPython.noop),
    ]
