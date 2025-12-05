# ProjectNote Data Migration Guide

## Problem
The `ProjectNote` model structure has changed:
- **Old**: `name` (CharField) + `body` (TextField)
- **New**: `content` (TextField)

## Solution Options

### Option 1: Simple Migration (Loses Old Data)
If you don't need to preserve existing notes:
```bash
python manage.py makemigrations project
python manage.py migrate
```

### Option 2: Data Migration (Preserves Old Data)
If you need to preserve existing notes, create a data migration:

1. Create migration file:
```bash
python manage.py makemigrations project --empty --name migrate_projectnote_data
```

2. Edit the created migration file and add:

```python
from django.db import migrations

def migrate_notes_forward(apps, schema_editor):
    """Migrate old name+body to new content field"""
    ProjectNote = apps.get_model('project', 'ProjectNote')
    
    for note in ProjectNote.objects.all():
        # Combine name and body into content
        content_parts = []
        if hasattr(note, 'name') and note.name:
            content_parts.append(note.name)
        if hasattr(note, 'body') and note.body:
            content_parts.append(note.body)
        
        note.content = '\n\n'.join(content_parts) if content_parts else 'Migrated note'
        note.save()

def migrate_notes_backward(apps, schema_editor):
    """Reverse migration - split content back to name+body"""
    ProjectNote = apps.get_model('project', 'ProjectNote')
    
    for note in ProjectNote.objects.all():
        if hasattr(note, 'content') and note.content:
            # Split content: first line = name, rest = body
            lines = note.content.split('\n\n', 1)
            note.name = lines[0][:255] if lines else 'Note'
            note.body = lines[1] if len(lines) > 1 else ''
            note.save()

class Migration(migrations.Migration):
    dependencies = [
        ('project', '0002_projectfile_projectnote'),  # Adjust to your latest migration
    ]

    operations = [
        # First, add the new content field (nullable)
        migrations.AddField(
            model_name='projectnote',
            name='content',
            field=models.TextField(null=True, blank=True),
        ),
        # Migrate data
        migrations.RunPython(migrate_notes_forward, migrate_notes_backward),
        # Remove old fields
        migrations.RemoveField(model_name='projectnote', name='name'),
        migrations.RemoveField(model_name='projectnote', name='body'),
        # Make content required
        migrations.AlterField(
            model_name='projectnote',
            name='content',
            field=models.TextField(),
        ),
        # Add timestamps if not already there
        migrations.AddField(
            model_name='projectnote',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='projectnote',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
```

3. Run migrations:
```bash
python manage.py migrate
```

## After Migration

Update or remove old note views if they're still being used:
- `project/views.py`: `add_note`, `note_detail`, `note_edit`, `note_delete`
- These views reference `name` and `body` which no longer exist

Or simply remove these views if you're using only the new API-based notepad widget.

