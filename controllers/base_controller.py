from flask import render_template
from typing import Dict, Any

class BaseController:
    """Base controller class that provides common functionality for all controllers."""
    
    def __init__(self):
        self.template_data: Dict[str, Any] = {}
    
    def render(self, template_name: str, **kwargs) -> str:
        """
        Render a template with the given data.
        
        Args:
            template_name: Name of the template to render
            **kwargs: Additional template variables
            
        Returns:
            Rendered template as string
        """
        # Merge instance template data with passed kwargs
        template_data = {**self.template_data, **kwargs}
        return render_template(template_name, **template_data)
    
    def add_template_data(self, key: str, value: Any) -> None:
        """
        Add data to be included in all template renders.
        
        Args:
            key: Template variable name
            value: Template variable value
        """
        self.template_data[key] = value
    
    def clear_template_data(self) -> None:
        """Clear all template data."""
        self.template_data.clear() 