from django.db.backends.mysql.base import DatabaseWrapper as BaseDatabaseWrapper
from django.db.backends.mysql.validation import DatabaseValidation as BaseValidation
from django.db.backends.mysql.features import DatabaseFeatures as BaseFeatures


class DatabaseValidation(BaseValidation):
    def check_database_version_supported(self):
        """Skip MariaDB version checking for compatibility."""
        pass


class DatabaseFeatures(BaseFeatures):
    @property
    def minimum_database_version(self):
        # Always return a supported version to bypass version checking
        return (5, 7)
    
    @property 
    def can_return_columns_from_insert(self):
        # MariaDB 10.4 doesn't support RETURNING clause properly
        return False


class DatabaseWrapper(BaseDatabaseWrapper):
    validation_class = DatabaseValidation
    features_class = DatabaseFeatures
    
    def get_connection_params(self):
        kwargs = super().get_connection_params()
        # Add MariaDB specific options
        kwargs.setdefault('charset', 'utf8mb4')
        kwargs.setdefault('use_unicode', True)
        return kwargs
