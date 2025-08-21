# my_metadata_loader.py
import json
import os
from typing import Tuple
import config

class MyMetadataLoader:
    """Handles metadata loading and content extraction from Migration Act pages"""
    
    def __init__(self):
        self.hashmap = None
    
    def load_hashmap(self):
        """Load the hashmap from JSON file"""
        try:
            with open(config.HASHMAP_PATH, "r", encoding="utf-8") as f:
                self.hashmap = json.load(f)
            print("✅ Hashmap loaded successfully")
            return self.hashmap
        except Exception as e:
            print(f"❌ Failed to load hashmap: {str(e)}")
            return None
    
    def _normalize_section_name(self, section_name_on_search_tree: str) -> str:
        """
        Convert section name from search tree format to hashmap format.
        
        Args:
            section_name_on_search_tree: Format like "Section name_code_vol_id"
        
        Returns:
            str: Normalized format like "Section name_code_vol"
        """
        parts = section_name_on_search_tree.split("_")
        # Remove the last part (ID) and rejoin
        return "_".join(parts[:-1])
    
    def get_page_range(self, section_name_on_search_tree: str) -> Tuple[int, int]:
        """
        Get start and end page numbers for a section.
        
        Args:
            section_name_on_search_tree: Section name from search tree
        
        Returns:
            Tuple[int, int]: (start_page, end_page)
        """
        if self.hashmap is None:
            self.load_hashmap()
        
        normalized_section_name = self._normalize_section_name(section_name_on_search_tree)
        
        try:
            section_data = self.hashmap[normalized_section_name]
            start_page = section_data[config.START_PAGE_KEY]
            end_page = section_data[config.END_PAGE_KEY]
            return (start_page, end_page)
        except KeyError as e:
            print(f"❌ Section not found in hashmap: {normalized_section_name}")
            raise e
    
    def extract_section_code(self, section_name_on_search_tree: str) -> str:
        """Extract section code from section name"""
        parts = section_name_on_search_tree.split("_")
        if len(parts) >= 2:
            return parts[1]  # Second element is section code
        return ""
    
    def extract_volume_info(self, section_name_on_search_tree: str) -> str:
        """Extract volume information from section name"""
        parts = section_name_on_search_tree.split("_")
        if len(parts) >= 3:
            return parts[2]  # Third element is volume info
        return ""
    
    def get_volume_directory_path(self, section_name_on_search_tree: str) -> str:
        """
        Get the directory path for the volume containing the section.
        
        Args:
            section_name_on_search_tree: Section name from search tree
        
        Returns:
            str: Directory path like "Migration Act Content Pages Txt Format/volume 1"
        """
        vol_info = self.extract_volume_info(section_name_on_search_tree)
        # Extract volume number (last character of volume info)
        vol_number = vol_info[-1] if vol_info else "1"
        
        return os.path.join(config.MIGRATION_ACT_CONTENT_BASE, f"volume {vol_number}")
    
    def get_section_content(self, section_name_on_search_tree: str) -> str:
        """
        Get all page content for a specific section.
        
        Args:
            section_name_on_search_tree: Section name from search tree
        
        Returns:
            str: Combined content from all pages for the section
        """
        try:
            # Get directory path and page range
            directory_path = self.get_volume_directory_path(section_name_on_search_tree)
            start_page, end_page = self.get_page_range(section_name_on_search_tree)
            
            # Extract section metadata
            section_code = self.extract_section_code(section_name_on_search_tree)
            vol_info = self.extract_volume_info(section_name_on_search_tree)
            
            # Build content with header
            all_content = ""
            debug_line = "=" * 80
            newline = "\n"
            
            # Add debug header
            all_content += debug_line + newline
            all_content += f"From Page {start_page} to {end_page} of {vol_info}, Section {section_code}\n"
            all_content += debug_line + newline
            
            # Read and combine all pages
            for page in range(start_page, end_page + 1):
                page_file_path = os.path.join(directory_path, f"page_{page}.txt")
                
                try:
                    with open(page_file_path, "r", encoding="utf-8") as file:
                        content = file.read()
                        all_content += content + newline
                except FileNotFoundError:
                    print(f"⚠️ Page file not found: {page_file_path}")
                    continue
                except Exception as e:
                    print(f"❌ Error reading page {page}: {str(e)}")
                    continue
            
            return all_content
            
        except Exception as e:
            print(f"❌ Error getting section content: {str(e)}")
            return ""