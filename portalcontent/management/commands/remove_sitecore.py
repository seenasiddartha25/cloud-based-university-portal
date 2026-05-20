import os
import shutil
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Removes the portalcontent app safely after migration to portalcontent'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to remove the portalcontent app',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(self.style.WARNING(
                'This command will remove the portalcontent app from the project. '
                'Run with --confirm to proceed.'
            ))
            return
        
        try:
            # Get the base directory
            from django.conf import settings
            base_dir = settings.BASE_DIR
            
            # Remove the portalcontent app directory
            sitecore_dir = os.path.join(base_dir, 'portalcontent')
            if os.path.exists(sitecore_dir):
                shutil.rmtree(sitecore_dir)
                self.stdout.write(self.style.SUCCESS(f'Successfully removed {sitecore_dir}'))
            else:
                self.stdout.write(self.style.WARNING(f'Directory {sitecore_dir} does not exist'))
            
            # Remove portalcontent templates
            sitecore_templates = os.path.join(base_dir, 'templates', 'portalcontent')
            if os.path.exists(sitecore_templates):
                shutil.rmtree(sitecore_templates)
                self.stdout.write(self.style.SUCCESS(f'Successfully removed {sitecore_templates}'))
            else:
                self.stdout.write(self.style.WARNING(f'Directory {sitecore_templates} does not exist'))
            
            self.stdout.write(self.style.SUCCESS(
                'The portalcontent app has been removed. Make sure all references to "portalcontent" '
                'have been replaced with "portalcontent" in your code.'
            ))
            
        except Exception as e:
            raise CommandError(f'Error removing portalcontent app: {str(e)}')
