import base64
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="selenium-mcp",
    instructions="This is a selenium-mcp service.",
)

state = {"drivers": {}, "current_session": None}


def get_driver():
    if state["current_session"] not in state["drivers"]:
        raise Exception("No active browser session")
    return state["drivers"][state["current_session"]]


def generate_session_id(browser):
    return f"{browser}_{int(time.time() * 1000)}"


@mcp.tool()
def start_browser(browser: str, headless: bool = False, arguments: list[str] = None):
    """
    Start a browser (supports Chrome and Firefox)
    :param browser: Browser type ("chrome" or "firefox")
    :param headless: Whether to run in headless mode
    :param arguments: Additional startup arguments
    """
    try:
        if browser not in ["chrome", "firefox"]:
            raise ValueError("Unsupported browser type. Use 'chrome' or 'firefox'.")

        driver = None
        if browser == "chrome":
            chrome_options = ChromeOptions()
            if headless:
                chrome_options.add_argument("--headless=new")
            if arguments:
                for arg in arguments:
                    chrome_options.add_argument(arg)
            driver = webdriver.Chrome(options=chrome_options)

        elif browser == "firefox":
            firefox_options = FirefoxOptions()
            if headless:
                firefox_options.add_argument("--headless")
            if arguments:
                for arg in arguments:
                    firefox_options.add_argument(arg)
            driver = webdriver.Firefox(options=firefox_options)

        session_id = generate_session_id(browser)
        state["drivers"][session_id] = driver
        state["current_session"] = session_id

        return f"Browser started with session_id: {session_id}"

    except Exception as e:
        return f"Error starting browser: {str(e)}"


@mcp.tool()
def navigate(url: str):
    """
    Navigates the browser to a specified URL.
    :param url: The URL to navigate to.
    """
    try:
        driver = get_driver()

        driver.get(url)

        return f"Navigated to {url}"

    except Exception as e:
        return f"Error navigating: {str(e)}"


@mcp.tool()
def close_session():
    """
    Close the current browser session
    """
    try:
        driver = get_driver()
        driver.quit()
        session_id = state["current_session"]
        del state["drivers"][session_id]
        state["current_session"] = None
        return f"Browser session {session_id} closed"
    except Exception as e:
        return f"Error closing session: {str(e)}"


@mcp.tool()
def find_element(by: str, value: str, timeout: int = 10000):
    """
    Finds an element on the page.
    :param by: Locator strategy to find the element (e.g., "id", "css", "xpath", etc.).
    :param value: The value for the locator strategy.
    :param timeout: Maximum time to wait for the element in milliseconds (default: 10000ms).
    """
    try:
        driver = get_driver()
        timeout_seconds = timeout / 1000

        element = WebDriverWait(driver, timeout_seconds).until(
            EC.presence_of_element_located((get_locator(by), value))
        )

        return f"Element found using {by}='{value}'"

    except Exception as e:
        return f"Error finding element: {str(e)}"


def get_locator(by: str):
    """
    Maps the locator strategy to Selenium's By class.
    :param by: Locator strategy (e.g., "id", "css", "xpath", etc.).
    :return: Corresponding Selenium By object.
    """
    locator_map = {
        "id": By.ID,
        "css": By.CSS_SELECTOR,
        "xpath": By.XPATH,
        "name": By.NAME,
        "tag": By.TAG_NAME,
        "class": By.CLASS_NAME,
    }
    if by.lower() not in locator_map:
        raise ValueError(f"Unsupported locator strategy: {by}")
    return locator_map[by.lower()]


@mcp.tool()
def click_element(by: str, value: str, timeout: int = 10000):
    """
    Clicks an element on the page.
    :param by: Locator strategy (e.g., "id", "css", "xpath", etc.).
    :param value: The value for the locator strategy.
    :param timeout: Maximum time to wait for the element in milliseconds (default: 10000ms).
    """
    try:
        driver = get_driver()
        timeout_seconds = timeout / 1000

        element = WebDriverWait(driver, timeout_seconds).until(
            EC.element_to_be_clickable((get_locator(by), value))
        )
        element.click()

        return f"Element clicked using {by}='{value}'"

    except Exception as e:
        return f"Error clicking element: {str(e)}"


@mcp.tool()
def send_keys(by: str, value: str, text: str, timeout: int = 10000):
    """
    Sends keys to an element (typing).
    :param by: Locator strategy (e.g., "id", "css", "xpath", etc.).
    :param value: The value for the locator strategy.
    :param text: The text to send to the element.
    :param timeout: Maximum time to wait for the element in milliseconds (default: 10000ms).
    """
    try:
        driver = get_driver()
        timeout_seconds = timeout / 1000

        element = WebDriverWait(driver, timeout_seconds).until(
            EC.presence_of_element_located((get_locator(by), value))
        )
        element.clear()
        element.send_keys(text)

        return f"Text '{text}' entered into element using {by}='{value}'"

    except Exception as e:
        return f"Error entering text: {str(e)}"


@mcp.tool()
def get_element_text(by: str, value: str, timeout: int = 10000):
    """
    Gets the text of an element.
    :param by: Locator strategy (e.g., "id", "css", "xpath", etc.).
    :param value: The value for the locator strategy.
    :param timeout: Maximum time to wait for the element in milliseconds (default: 10000ms).
    """
    try:
        driver = get_driver()
        timeout_seconds = timeout / 1000

        element = WebDriverWait(driver, timeout_seconds).until(
            EC.presence_of_element_located((get_locator(by), value))
        )
        text = element.text

        return f"Text of element using {by}='{value}': {text}"

    except Exception as e:
        return f"Error getting element text: {str(e)}"


@mcp.tool()
def hover(by: str, value: str, timeout: int = 10000):
    """
    Hovers over an element.
    :param by: Locator strategy (e.g., "id", "css", "xpath", etc.).
    :param value: The value for the locator strategy.
    :param timeout: Maximum time to wait for the element in milliseconds (default: 10000ms).
    """
    try:
        driver = get_driver()
        timeout_seconds = timeout / 1000

        element = WebDriverWait(driver, timeout_seconds).until(
            EC.presence_of_element_located((get_locator(by), value))
        )
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()

        return f"Hovered over element using {by}='{value}'"

    except Exception as e:
        return f"Error hovering over element: {str(e)}"


@mcp.tool()
def drag_and_drop(
    by: str, value: str, target_by: str, target_value: str, timeout: int = 10000
):
    """
    Drags an element and drops it onto another element.
    :param by: Locator strategy for the source element.
    :param value: The value for the source locator strategy.
    :param target_by: Locator strategy for the target element.
    :param target_value: The value for the target locator strategy.
    :param timeout: Maximum time to wait for the elements in milliseconds (default: 10000ms).
    """
    try:
        driver = get_driver()
        timeout_seconds = timeout / 1000

        source_element = WebDriverWait(driver, timeout_seconds).until(
            EC.presence_of_element_located((get_locator(by), value))
        )
        target_element = WebDriverWait(driver, timeout_seconds).until(
            EC.presence_of_element_located((get_locator(target_by), target_value))
        )

        actions = ActionChains(driver)
        actions.drag_and_drop(source_element, target_element).perform()

        return f"Drag and drop completed from {by}='{value}' to {target_by}='{target_value}'"

    except Exception as e:
        return f"Error performing drag and drop: {str(e)}"


@mcp.tool()
def double_click(by: str, value: str, timeout: int = 10000):
    """
    Performs a double click on an element.
    :param by: Locator strategy (e.g., "id", "css", "xpath", etc.).
    :param value: The value for the locator strategy.
    :param timeout: Maximum time to wait for the element in milliseconds (default: 10000ms).
    """
    try:
        driver = get_driver()
        timeout_seconds = timeout / 1000

        element = WebDriverWait(driver, timeout_seconds).until(
            EC.presence_of_element_located((get_locator(by), value))
        )
        actions = ActionChains(driver)
        actions.double_click(element).perform()

        return f"Double click performed on element using {by}='{value}'"

    except Exception as e:
        return f"Error performing double click: {str(e)}"


@mcp.tool()
def right_click(by: str, value: str, timeout: int = 10000):
    """
    Performs a right click (context click) on an element.
    :param by: Locator strategy (e.g., "id", "css", "xpath", etc.).
    :param value: The value for the locator strategy.
    :param timeout: Maximum time to wait for the element in milliseconds (default: 10000ms).
    """
    try:
        driver = get_driver()
        timeout_seconds = timeout / 1000

        element = WebDriverWait(driver, timeout_seconds).until(
            EC.presence_of_element_located((get_locator(by), value))
        )
        actions = ActionChains(driver)
        actions.context_click(element).perform()

        return f"Right click performed on element using {by}='{value}'"

    except Exception as e:
        return f"Error performing right click: {str(e)}"


@mcp.tool()
def press_key(key: str):
    """
    Simulates pressing a keyboard key.
    :param key: Key to press (e.g., "Enter", "Tab", "a", etc.).
    """
    try:
        driver = get_driver()
        actions = ActionChains(driver)
        actions.key_down(key).key_up(key).perform()

        return f"Key '{key}' pressed"

    except Exception as e:
        return f"Error pressing key: {str(e)}"


@mcp.tool()
def upload_file(by: str, value: str, file_path: str, timeout: int = 10000):
    """
    Uploads a file using a file input element.
    :param by: Locator strategy (e.g., "id", "css", "xpath", etc.).
    :param value: The value for the locator strategy.
    :param file_path: Absolute path to the file to upload.
    :param timeout: Maximum time to wait for the element in milliseconds (default: 10000ms).
    """
    try:
        driver = get_driver()
        timeout_seconds = timeout / 1000

        element = WebDriverWait(driver, timeout_seconds).until(
            EC.presence_of_element_located((get_locator(by), value))
        )
        element.send_keys(file_path)

        return f"File upload initiated using {by}='{value}'"

    except Exception as e:
        return f"Error uploading file: {str(e)}"


@mcp.tool()
def take_screenshot(output_path: str = None):
    """
    Captures a screenshot of the current page.
    :param output_path: Optional path where to save the screenshot. If not provided, returns base64 data.
    """
    try:
        driver = get_driver()
        screenshot = driver.get_screenshot_as_base64()

        if output_path:
            with open(output_path, "wb") as file:
                file.write(base64.b64decode(screenshot))
            return f"Screenshot saved to {output_path}"
        else:
            return f"Screenshot captured as base64: {screenshot}"

    except Exception as e:
        return f"Error taking screenshot: {str(e)}"


@mcp.tool()
def close_session():
    """
    Closes the current browser session.
    """
    try:
        driver = get_driver()
        driver.quit()
        session_id = state["current_session"]
        del state["drivers"][session_id]
        state["current_session"] = None

        return f"Browser session {session_id} closed"

    except Exception as e:
        return f"Error closing session: {str(e)}"


def cleanup():
    """
    Cleans up all active browser sessions.
    """
    for session_id, driver in state["drivers"].items():
        try:
            driver.quit()
        except Exception as e:
            print(f"Error closing browser session {session_id}: {e}")
    state["drivers"].clear()
    state["current_session"] = None
