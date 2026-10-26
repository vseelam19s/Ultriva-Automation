using OpenQA.Selenium;
using OpenQA.Selenium.Chrome;
using OpenQA.Selenium.Support.UI;

namespace ultriva_selenium_csharp;

public class Tests
{
    private const string LoginUrl = "https://engineering.ultrivalms.com/qals1011";
    private const string UserName = "buyeruser";
    private const string Password = "Ultriva!23";
    private static readonly bool KeepBrowserOpenAfterTest = true;

    private IWebDriver? _driver;
    private WebDriverWait? _wait;

    [SetUp]
    public void Setup()
    {
        // Use a unique temp profile per test so no session/cookie bleed between runs.
        var profileDir = Path.Combine(Path.GetTempPath(), $"ultriva_chrome_{TestContext.CurrentContext.Test.ID}");
        Directory.CreateDirectory(profileDir);

        var options = new ChromeOptions();
        options.AddArgument("start-maximized");
        options.AddArgument($"--user-data-dir={profileDir}");
        if (KeepBrowserOpenAfterTest)
        {
            options.LeaveBrowserRunning = true;
        }

        _driver = new ChromeDriver(options);
        _wait   = new WebDriverWait(_driver, TimeSpan.FromSeconds(30));
    }

    [TearDown]
    public void TearDown()
    {
        try
        {
            if (_driver != null)
            {
                Directory.CreateDirectory("TestResults");
                var screenshotPath = Path.Combine("TestResults", $"login-result-{DateTime.Now:yyyyMMdd-HHmmss}.png");
                ((ITakesScreenshot)_driver).GetScreenshot().SaveAsFile(screenshotPath);
                TestContext.WriteLine($"Screenshot saved: {Path.GetFullPath(screenshotPath)}");
            }
        }
        catch
        {
            // Ignore screenshot failures during cleanup.
        }
        finally
        {
            _driver?.Quit();
            _driver?.Dispose();

            if (KeepBrowserOpenAfterTest)
            {
                TestContext.Out.WriteLine("Browser left open by configuration (KeepBrowserOpenAfterTest=true).");
            }
        }
    }

    // ──────────────────────────────────────────────
    // Helper: performs the login steps and asserts success.
    // ──────────────────────────────────────────────
    private void PerformLogin()
    {
        _driver!.Navigate().GoToUrl(LoginUrl);

        var usernameInput = _wait!.Until(d => d.FindElement(By.Id("UserName")));
        var passwordInput = _driver.FindElement(By.Id("Password"));
        var loginButton   = _driver.FindElement(By.Id("login-button"));

        usernameInput.Clear();
        usernameInput.SendKeys(UserName);
        passwordInput.Clear();
        passwordInput.SendKeys(Password);
        loginButton.Click();

        _wait.Until(d =>
        {
            var urlChanged       = !string.Equals(d.Url.TrimEnd('/'), LoginUrl.TrimEnd('/'), StringComparison.OrdinalIgnoreCase);
            var invalidLoginShown = d.PageSource.Contains("Invalid username or password", StringComparison.OrdinalIgnoreCase);
            return urlChanged || invalidLoginShown;
        });

        Assert.That(_driver.Url.TrimEnd('/'), Is.Not.EqualTo(LoginUrl.TrimEnd('/')),
            "Login did not move away from the login page.");
    }

    // ──────────────────────────────────────────────
    // Test 1: Login only – stays on the home page.
    // ──────────────────────────────────────────────
    [Test]
    public void Login_With_Valid_Credentials_Should_Navigate_To_Home_Page()
    {
        Assert.That(_driver, Is.Not.Null);
        Assert.That(_wait,   Is.Not.Null);

        PerformLogin();

        // Verify we landed on the home / landing page.
        Assert.That(_driver!.Url, Does.Contain("/QALS1011").IgnoreCase,
            "URL after login does not contain the app path.");
    }

    // ──────────────────────────────────────────────
    // Test 2: Login then Logout – returns to login.
    // ──────────────────────────────────────────────
    [Test]
    public void Login_Then_Logout_Should_Return_To_Login_Page()
    {
        Assert.That(_driver, Is.Not.Null);
        Assert.That(_wait,   Is.Not.Null);

        PerformLogin();

        // Open the avatar/user menu, then click Logout.
        var avatarButtons = _driver!.FindElements(By.CssSelector("button.avatar-btn"));
        if (avatarButtons.Count > 0)
            avatarButtons[0].Click();

        var logoutLink = _wait!.Until(d =>
        {
            var links = d.FindElements(By.CssSelector("a[href*='/Account/Logout']"));
            return links.Count > 0 ? links[0] : null;
        });

        Assert.That(logoutLink, Is.Not.Null, "Logout link was not found after login.");
        logoutLink!.Click();

        _wait.Until(d => d.Url.Contains("/qals1011", StringComparison.OrdinalIgnoreCase));

        var userNameField = _wait.Until(d => d.FindElement(By.Id("UserName")));
        Assert.That(userNameField.Displayed, Is.True,
            "UserName input was not visible after logout – login page did not reload.");
    }
}
