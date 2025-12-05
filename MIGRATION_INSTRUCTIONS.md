# Migration Instructions

## ✅ Ready to Run Migrations

The migrations have been properly set up to handle the data migration from old ProjectNote structure to new one. Here's what will happen:

### Migration Order:
1. **0003_migrate_projectnote_to_content**: 
   - Adds new `content`, `created_at`, `updated_at` fields to ProjectNote
   - Migrates existing data from `name` + `body` → `content`
   - Removes old `name` and `body` fields

2. **0004_comment_reminder_sharelink...**: 
   - Creates new models: Comment, Reminder, ShareLink
   - Adds new fields to Project model (start_date, end_date, timestamps)
   - Adds all indexes

## Run the Migrations:

```bash
python manage.py migrate
```

This will:
- Run authtoken migrations (for DRF token authentication)
- Migrate your existing ProjectNote data safely
- Create all new models and fields

## What Happens to Existing Notes:

If you have existing notes with `name` and `body` fields, they will be automatically combined:
- `name` + `body` → Combined into `content` field
- Format: `name\n\nbody` (if both exist)
- If only one exists, just that value will be used
- If both are empty, it will set "Migrated note" as fallback

## After Migration:

1. **Test the features**: Visit any project page and try:
   - Share Project button
   - Notepad widget
   - Comments widget  
   - Reminders widget

2. **Verify data**: Check that your existing notes were migrated correctly

3. **Optional - Make content required**: If you want to make the `content` field required (non-nullable), you can create another migration after verifying everything works.

## Troubleshooting:

If you encounter any issues:

1. **Check migration status**:
   ```bash
   python manage.py showmigrations project
   ```

2. **See migration plan**:
   ```bash
   python manage.py migrate --plan
   ```

3. **Rollback if needed** (be careful!):
   ```bash
   python manage.py migrate project 0002_projectfile_projectnote
   ```

## Next Steps After Migration:

1. Install dependencies (if not already done):
   ```bash
   pip install -r requirements.txt
   ```

2. Collect static files (for production):
   ```bash
   python manage.py collectstatic
   ```

3. Create a superuser token for API testing (optional):
   ```python
   python manage.py shell
   >>> from rest_framework.authtoken.models import Token
   >>> from account.models import User
   >>> user = User.objects.first()
   >>> token, created = Token.objects.get_or_create(user=user)
   >>> print(f"Token: {token.key}")
   ```

---

**Ready to proceed?** Just run: `python manage.py migrate`

