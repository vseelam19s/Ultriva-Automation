import java.time.Duration;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.Select;
import org.openqa.selenium.support.ui.WebDriverWait;

public class AttachNotesPopup {

    public static void fillNotesAndApply(WebDriver driver, String noteTitle, String noteDescription) {
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));

        // Wait for the modal popup heading to appear.
        wait.until(ExpectedConditions.visibilityOfElementLocated(
            By.xpath("//*[contains(normalize-space(.), 'Attach notes for Card')] | //*[@role='dialog' and contains(., 'Attach notes')]")
        ));

        // Select a note title from the Notes dropdown.
        WebElement noteDropdown = wait.until(ExpectedConditions.elementToBeClickable(
            By.xpath("//label[contains(normalize-space(.), 'Notes')]/following::select[1] | //select[contains(@name, 'note') or contains(@id, 'note') or contains(@class, 'note')] | //select")
        ));
        Select selectNote = new Select(noteDropdown);
        if (noteTitle != null && !noteTitle.trim().isEmpty()) {
            selectNote.selectByVisibleText(noteTitle);
        }

        // Enter note description.
        WebElement noteTextArea = wait.until(ExpectedConditions.visibilityOfElementLocated(
            By.xpath("//textarea[contains(@name, 'note') or contains(@id, 'note') or contains(@class, 'note')] | //input[contains(@name, 'note') or contains(@id, 'note') or contains(@class, 'note')][@type='text']")
        ));
        noteTextArea.clear();
        noteTextArea.sendKeys(noteDescription);

        // Check the apply-to-all checkbox.
        WebElement applyToAllCheckbox = wait.until(ExpectedConditions.presenceOfElementLocated(
            By.xpath("//label[contains(normalize-space(.), 'Apply this notes and priority to all selected Cards')]//input[@type='checkbox'] | //input[@type='checkbox' and contains(@id, 'ApplyNotesToAll')] | //input[@type='checkbox' and contains(@name, 'ApplyNotesToAll')] | //label[contains(normalize-space(.), 'Apply this notes and priority to all selected Cards')] | //input[@type='checkbox'][following-sibling::*[contains(normalize-space(.), 'Apply this notes')]]")
        ));

        if (!applyToAllCheckbox.isSelected()) {
            applyToAllCheckbox.click();
        }
    }
}
