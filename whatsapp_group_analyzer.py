#!/usr/bin/env python3
"""
WhatsApp Group Member Intersection Analyzer

This script allows you to:
1. Authenticate with WhatsApp Web
2. View all your groups
3. Select multiple groups
4. Find members that are common to all selected groups
5. Export results to a CSV file
"""

import os
import time
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import json

class WhatsAppGroupAnalyzer:
    def __init__(self):
        self.driver = None
        self.groups = []
        
    def setup_driver(self):
        """Initialize Chrome WebDriver with appropriate options"""
        print("Setting up WhatsApp Web connection...")
        print("(Installing/updating ChromeDriver if needed...)")
        
        chrome_options = Options()
        chrome_options.add_argument("--user-data-dir=/tmp/whatsapp_session")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.get("https://web.whatsapp.com")
        
    def wait_for_login(self):
        """Wait for user to scan QR code and login"""
        print("\n" + "="*60)
        print("Please scan the QR code with your WhatsApp mobile app")
        print("="*60 + "\n")
        
        try:
            # Wait for the main page to load (search box appears after login)
            WebDriverWait(self.driver, 120).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
            )
            print("✓ Successfully logged in to WhatsApp Web!\n")
            time.sleep(3)  # Give it time to fully load
            return True
        except TimeoutException:
            print("✗ Login timeout. Please try again.")
            return False
    
    def get_all_groups(self):
        """Retrieve all WhatsApp groups"""
        print("Fetching your groups...")
        time.sleep(2)
        
        groups = []
        
        try:
            # Click on the menu button
            menu_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@aria-label="Menu"]'))
            )
            menu_button.click()
            time.sleep(1)
            
            # Look for "New group" option to navigate
            # Alternative: directly search for groups in the chat list
            self.driver.get("https://web.whatsapp.com")
            time.sleep(3)
            
            # Get all chat elements
            chat_elements = self.driver.find_elements(By.XPATH, '//div[@role="listitem"]')
            
            for idx, chat in enumerate(chat_elements):
                try:
                    # Click on the chat to open it
                    chat.click()
                    time.sleep(0.5)
                    
                    # Check if it's a group by looking for group info
                    try:
                        header = self.driver.find_element(By.XPATH, '//header')
                        header.click()
                        time.sleep(1)
                        
                        # Check if participant list exists (indicates it's a group)
                        try:
                            participants_section = self.driver.find_element(
                                By.XPATH, 
                                '//div[contains(@class, "participants")]|//div[contains(text(), "participants")]|//div[contains(text(), "participant")]'
                            )
                            
                            # Get group name
                            group_name_elem = self.driver.find_element(
                                By.XPATH, 
                                '//div[@role="button"]//span[@dir="auto"]'
                            )
                            group_name = group_name_elem.text
                            
                            if group_name and group_name not in [g['name'] for g in groups]:
                                groups.append({
                                    'name': group_name,
                                    'members': []
                                })
                                print(f"  Found group: {group_name}")
                            
                            # Close the group info
                            close_button = self.driver.find_element(By.XPATH, '//div[@aria-label="Close"]')
                            close_button.click()
                            time.sleep(0.3)
                            
                        except NoSuchElementException:
                            # Not a group, skip
                            # Close any open panel
                            try:
                                close_button = self.driver.find_element(By.XPATH, '//div[@aria-label="Close"]')
                                close_button.click()
                            except:
                                pass
                            time.sleep(0.3)
                    except:
                        pass
                        
                except Exception as e:
                    continue
            
            self.groups = groups
            return groups
            
        except Exception as e:
            print(f"Error fetching groups: {e}")
            return []
    
    def get_group_members(self, group_name):
        """Get all members of a specific group"""
        print(f"Fetching members for: {group_name}...")
        
        try:
            # Go back to main page
            self.driver.get("https://web.whatsapp.com")
            time.sleep(2)
            
            # Search for the group
            search_box = self.driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
            search_box.clear()
            search_box.send_keys(group_name)
            time.sleep(2)
            
            # Click on the first result
            first_result = self.driver.find_element(By.XPATH, '//div[@role="listitem"]')
            first_result.click()
            time.sleep(1)
            
            # Click on header to open group info
            header = self.driver.find_element(By.XPATH, '//header')
            header.click()
            time.sleep(2)
            
            # Scroll to load all participants
            participants_container = self.driver.find_element(
                By.XPATH, 
                '//div[contains(@class, "participants")]|//div[@role="list"]'
            )
            
            # Scroll multiple times to load all members
            for _ in range(10):
                self.driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight", 
                    participants_container
                )
                time.sleep(0.5)
            
            # Get all participant elements
            member_elements = self.driver.find_elements(
                By.XPATH, 
                '//div[@role="listitem"]//span[@dir="auto"]'
            )
            
            members = []
            for member_elem in member_elements:
                member_name = member_elem.text.strip()
                if member_name and member_name not in members:
                    members.append(member_name)
            
            # Close group info
            close_button = self.driver.find_element(By.XPATH, '//div[@aria-label="Close"]')
            close_button.click()
            time.sleep(0.5)
            
            print(f"  Found {len(members)} members")
            return members
            
        except Exception as e:
            print(f"Error fetching members for {group_name}: {e}")
            return []
    
    def display_groups_and_select(self):
        """Display groups and let user select which ones to analyze"""
        if not self.groups:
            print("No groups found!")
            return []
        
        print("\n" + "="*60)
        print("YOUR WHATSAPP GROUPS")
        print("="*60 + "\n")
        
        for idx, group in enumerate(self.groups, 1):
            print(f"{idx}. {group['name']}")
        
        print("\n" + "="*60)
        print("Enter the numbers of groups to analyze (comma-separated)")
        print("Example: 1,3,5 or 1-3,5,7-9")
        print("="*60 + "\n")
        
        while True:
            selection = input("Your selection: ").strip()
            
            try:
                selected_indices = self.parse_selection(selection, len(self.groups))
                if selected_indices:
                    selected_groups = [self.groups[i] for i in selected_indices]
                    
                    print("\nYou selected:")
                    for group in selected_groups:
                        print(f"  • {group['name']}")
                    
                    confirm = input("\nProceed with these groups? (yes/no): ").strip().lower()
                    if confirm in ['yes', 'y']:
                        return selected_groups
                    else:
                        print("\nPlease make your selection again.")
                else:
                    print("No valid groups selected. Try again.")
            except Exception as e:
                print(f"Invalid selection: {e}. Please try again.")
    
    def parse_selection(self, selection, max_num):
        """Parse user selection string (e.g., '1,3,5' or '1-3,5')"""
        indices = set()
        parts = selection.split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                start, end = part.split('-')
                start, end = int(start.strip()), int(end.strip())
                indices.update(range(start-1, end))
            else:
                indices.add(int(part.strip()) - 1)
        
        # Filter valid indices
        valid_indices = [i for i in indices if 0 <= i < max_num]
        return sorted(valid_indices)
    
    def find_intersection(self, selected_groups):
        """Find members common to all selected groups"""
        print("\n" + "="*60)
        print("ANALYZING GROUP MEMBERS")
        print("="*60 + "\n")
        
        # Fetch members for each selected group
        for group in selected_groups:
            members = self.get_group_members(group['name'])
            group['members'] = members
        
        # Find intersection
        if not selected_groups:
            return []
        
        common_members = set(selected_groups[0]['members'])
        
        for group in selected_groups[1:]:
            common_members = common_members.intersection(set(group['members']))
        
        return list(common_members)
    
    def export_to_csv(self, selected_groups, common_members):
        """Export results to CSV file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"whatsapp_group_intersection_{timestamp}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['Analysis Results'])
            writer.writerow(['Timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            writer.writerow([])
            
            # Write selected groups
            writer.writerow(['Selected Groups'])
            for group in selected_groups:
                writer.writerow([group['name'], f"{len(group['members'])} members"])
            writer.writerow([])
            
            # Write common members
            writer.writerow(['Common Members', f"Total: {len(common_members)}"])
            writer.writerow(['Name'])
            for member in sorted(common_members):
                writer.writerow([member])
            
            writer.writerow([])
            writer.writerow(['Detailed Group Membership'])
            
            # Create detailed comparison
            all_members = set()
            for group in selected_groups:
                all_members.update(group['members'])
            
            # Header row with group names
            header = ['Member Name'] + [group['name'] for group in selected_groups]
            writer.writerow(header)
            
            # Write each member and their membership status
            for member in sorted(all_members):
                row = [member]
                for group in selected_groups:
                    row.append('✓' if member in group['members'] else '✗')
                writer.writerow(row)
        
        return filename
    
    def run(self):
        """Main execution flow"""
        try:
            # Setup and login
            self.setup_driver()
            
            if not self.wait_for_login():
                return
            
            # Get all groups
            groups = self.get_all_groups()
            
            if not groups:
                print("No groups found or error occurred.")
                return
            
            print(f"\n✓ Found {len(groups)} groups\n")
            
            # Let user select groups
            selected_groups = self.display_groups_and_select()
            
            if not selected_groups:
                print("No groups selected. Exiting.")
                return
            
            # Find common members
            common_members = self.find_intersection(selected_groups)
            
            # Display results
            print("\n" + "="*60)
            print("RESULTS")
            print("="*60 + "\n")
            
            if common_members:
                print(f"Found {len(common_members)} common member(s):\n")
                for member in sorted(common_members):
                    print(f"  • {member}")
            else:
                print("No common members found across all selected groups.")
            
            # Export to CSV
            print("\nExporting results...")
            filename = self.export_to_csv(selected_groups, common_members)
            print(f"✓ Results exported to: {filename}")
            
            print("\n" + "="*60)
            print("Analysis complete!")
            print("="*60)
            
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.driver:
                input("\nPress Enter to close the browser...")
                self.driver.quit()


def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║     WhatsApp Group Member Intersection Analyzer           ║
╚════════════════════════════════════════════════════════════╝

This tool will help you find members that are common across
multiple WhatsApp groups.

Requirements:
  - Google Chrome browser installed
  - Selenium WebDriver for Chrome
  - Active WhatsApp account

""")
    
    input("Press Enter to start...")
    
    analyzer = WhatsAppGroupAnalyzer()
    analyzer.run()


if __name__ == "__main__":
    main()

