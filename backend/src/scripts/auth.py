from playwright.async_api import Page, BrowserContext
from json import load, loads, dump, dumps
import asyncio
import random

class Authenticate:
    STATE_FILE = "src/sessions/browser_state_2.json"
    
    def __init__(self, username, password, page: Page, context: BrowserContext):
        self.username = username
        self.password = password
        self.page = page
        self.context = context
    
    async def load_browser_state(self):
        '''
        Load saved data in form of browser state
        cookies, localStorage, sessionStorage and inject via init script
        '''
        try:
            with open(Authenticate.STATE_FILE, "r") as fs:
                state = load(fs)
            
            # Add cookies directly to the context
            if "cookies" in state:
                await self.context.add_cookies(state["cookies"])
            
            # Set up localStorage and sessionStorage via init script
            await self.context.add_init_script(
                f"""
                (() => {{
                    const localStorageData = {dumps(state.get('localStorage', {}))};
                    for (const key in localStorageData) {{
                        try {{
                            window.localStorage.setItem(key, localStorageData[key]);
                        }} catch(e) {{
                            console.error("Error setting localStorage", key, e);
                        }}
                    }}
                    
                    const sessionStorageData = {dumps(state.get('sessionStorage', {}))};
                    for (const key in sessionStorageData) {{
                        try {{
                            window.sessionStorage.setItem(key, sessionStorageData[key]);
                        }} catch(e) {{
                            console.error("Error setting sessionStorage", key, e);
                        }}
                    }}
                }})();
                """
            )
            print("Browser state loaded successfully")
            return True
        except FileNotFoundError:
            print("No previous browser state found")
            return False
        except Exception as e:
            print(f"Error loading browser state: {e}")
            return False
    
    async def save_browser_state(self):  # Fixed typo in method name
        '''
        Save the browser state
        '''
        # Navigate to Instagram domain to ensure we can access storage
        try:
            # Make sure we're on Instagram's domain
            current_url = self.page.url
            if not current_url.startswith("https://www.instagram.com"):
                await self.page.goto("https://www.instagram.com/")
            
            await self.page.wait_for_load_state("domcontentloaded")
            
            # Get cookies from context
            cookies = await self.context.cookies()
            
            # Try to extract localStorage and sessionStorage with error handling
            local_storage = {}
            session_storage = {}
            try:
                local_storage_str = await self.page.evaluate("() => JSON.stringify(window.localStorage)")
                local_storage = loads(local_storage_str)
            except Exception as e:
                print(f"Could not access localStorage: {e}")
            
            try:
                session_storage_str = await self.page.evaluate("() => JSON.stringify(window.sessionStorage)")
                session_storage = loads(session_storage_str)
            except Exception as e:
                print(f"Could not access sessionStorage: {e}")
            
            browser_state = {
                "cookies": cookies,
                "localStorage": local_storage,
                "sessionStorage": session_storage,
            }
            
            # Write state to file
            with open(Authenticate.STATE_FILE, "w") as f:
                dump(browser_state, f, indent=4)
            
            print("Browser state saved successfully")
            return True
        except Exception as e:
            print(f"Error saving browser state: {e}")
            return False
    
    async def __auth_process(self):
        try:
            await self.page.goto("https://www.instagram.com/accounts/login/")
            
            await self.page.wait_for_load_state("domcontentloaded")
            await self.page.type('input[name="username"]', self.username, delay = random.gammavariate(2.05678,1.032))
            await asyncio.sleep(random.random()*2.5)
            await self.page.type('input[name="password"]', self.password, delay = random.gammavariate(2.05678,1.032))
            await asyncio.sleep(random.random()*2.5)
            await self.page.click('button[type="submit"]',force=True)
            
            # Wait for navigation or confirmation, but with timeout
            try:
                await asyncio.wait_for(
                    self.page.wait_for_url("https://www.instagram.com/accounts/onetap/?next=%2F"),
                    timeout=30
                )
                # await self.page.get_by_text("Save info").click()
                await self.page.locator("button:has-text('Save info')").click()
                print("Login successful")
                return True
            except asyncio.TimeoutError:
                print("Login process timed out, checking if we're logged in anyway")
                # Check if we're logged in by looking for typical elements on Instagram's feed page
                if "instagram.com" in self.page.url and not "accounts/login" in self.page.url:
                    print("Appears to be logged in despite timeout")
                    return True
                return False
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    async def get_session(self):
        # First check for saved session
        loaded = await self.load_browser_state()
        # Check if we're already logged in after loading state
        try:
            await self.page.goto("https://www.instagram.com/")
            await self.page.wait_for_load_state("domcontentloaded")
            
            # Check if we see a login button/form
            login_button = await self.page.query_selector('input[name="username"]')
            if login_button or "accounts/login" in self.page.url:
                print("Session expired or not logged in, authenticating...")
                auth_success = await self.__auth_process()
                if not auth_success:
                    print("Authentication failed")
                    return False
            else:
                print("Already logged in, using existing session")
        except Exception as e:
            print(f"Error checking login status: {e}")
            auth_success = await self.__auth_process()
            if not auth_success:
                print("Authentication failed")
                return False
        
        # Save the updated browser state
        await self.save_browser_state()  # Fixed method name
        await asyncio.sleep(random.gammavariate(2.05678,1.032))
        return True