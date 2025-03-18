from django.contrib import admin
from django.urls import path

# Add register_view method to AdminSite if it doesn't exist
if not hasattr(admin.AdminSite, 'register_view'):
    def register_view(self, path, view, name=None):
        """
        Register a view function with the admin site.
        
        Args:
            path: The URL path within the admin site
            view: The view function
            name: The name for the URL pattern
        """
        self._registry_views = getattr(self, '_registry_views', {})
        self._registry_views[path] = (view, name)
        
        # Add the view to the url patterns
        urlpatterns = getattr(self, 'urlpatterns', None)
        if urlpatterns is not None:
            urlpatterns.append(
                path(path, self.admin_view(view), name=name)
            )
    
    admin.AdminSite.register_view = register_view