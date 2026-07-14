/**
 * Poll a queued Celery admin job until SUCCESS/FAILURE or timeout.
 * Used by the admin dashboard reminder and monthly-report buttons.
 */
import { api } from "../../api/client";

export async function runAdminCeleryJob(path, okText, showMsg) {
  const started = await api(path, { method: "POST" });
  showMsg(`${okText} Task: ${started.task_id}`, "info");
  for (let i = 0; i < 15; i++) {
    await new Promise((r) => setTimeout(r, 1000));
    const status = await api(`/api/jobs/tasks/${started.task_id}`);
    if (status.state === "SUCCESS") {
      const result = status.result || {};
      const emailed = result.emailed === true || result.delivery?.email === true;
      if (emailed) {
        showMsg(`${okText} Done. Email sent to MailHog (http://localhost:8025).`);
      } else if (result.emailed === false || result.delivery?.email === false) {
        showMsg(
          `${okText} Done, but email was not sent. Check SMTP_HOST and restart Celery if needed.`,
          "warning"
        );
      } else {
        showMsg(`${okText} Done.`);
      }
      return;
    }
    if (status.state === "FAILURE") {
      throw new Error(status.error || "Task failed");
    }
  }
  showMsg("Task still running. Check Celery worker logs.", "warning");
}
