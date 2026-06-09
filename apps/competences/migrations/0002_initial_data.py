from django.db import migrations


def populate_competences(apps, schema_editor):
    Competence = apps.get_model('competences', 'Competence')
    competences = [
        'Ménage', 'Jardinage', 'Livraison', 'Maçonnerie', 'Électricité',
        'Peinture', 'Cuisine', 'Lessive', 'Courses', 'Soutien scolaire',
        'Informatique', 'Secrétariat', 'Serveur', 'Accueil', 'Sécurité',
        'Garde d\'enfants', 'Soins aux personnes âgées', 'Plomberie',
        'Menuiserie', 'Déménagement',
    ]
    for nom in competences:
        Competence.objects.get_or_create(nom=nom)


class Migration(migrations.Migration):

    dependencies = [
        ('competences', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_competences, migrations.RunPython.noop),
    ]
