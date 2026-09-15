import streamlit as st
from abc import ABC, abstractmethod
from frontend.ui.theme import render_hero

class BaseVisualization(ABC):
    """
    Abstract base class for all Streamlit UI visualization pages.
    Enforces a standard structure for loading data, processing it, and rendering charts.
    """
    
    def __init__(self, title: str, description: str):
        self.title = title
        self.description = description

    def render_header(self):
        """Renders the standard page header."""
        render_hero(self.title, self.description, compact=True)

    @abstractmethod
    def load_data(self):
        """Load necessary data (e.g., from files, DB, or APIs)."""
        pass

    @abstractmethod
    def process_data(self):
        """Process the loaded data into a format suitable for plotting."""
        pass

    @abstractmethod
    def build_charts(self):
        """Construct and render the Streamlit/Plotly charts."""
        pass

    def render(self):
        """Executes the standard rendering pipeline."""
        self.render_header()
        
        try:
            self.load_data()
            self.process_data()
            self.build_charts()
        except Exception as e:
            st.error(f"Error rendering visualization '{self.title}': {e}")
